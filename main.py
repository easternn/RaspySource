source_path = '<PATH>'
import sys
sys.path.append(source_path + '/modules')

from datetime import datetime
import requests
import time
import collectors
import stat
from logger import logger

loop_period = 30
API_URL = '<API_URL>'
API_TOKEN = '<API_TOKEN>'


def Gather(log_namespace):
	"""
		Description:
			Gather data from collectors
		accept:
			log_namespace - for local logging
		return:
			success/fail (bool)
			time of execution (float)
			array of sensors in TVD format (list)
			array of read times of sensors (list)
	"""
	start = time.time()

	tvd = []
	rst = {}
	check = True

	check_collector_1, tvd_collector_1, rst_collector_1 = collectors.Collector_1(log_namespace + ":" + "temp-DS18B20", "temp-DS18B20", "SENSOR_temp-DS18B20_")
	tvd += tvd_collector_1
	rst.update(rst_collector_1)
	check = check and check_collector_1

	finish = time.time()
	logger.info(log_namespace + " - " + "Gather time: " + str(round(finish - start, 2)))
	return check, finish - start, tvd, rst

def ServerRequest(log_namespace, payload):
	"""
		Description:
			Sends payload to API_URL
		accept:
			logging namespace for logging, payload
		return:
			success/fail, time of sending request
	"""
	start = time.time()
	check = True

	try:
		resp = requests.post(API_URL, json=payload, headers = {
			"Content-type": "application/json",
			"Content-length": "<calculated when request is sent>",
			"Accept-encoding": "gzip, deflate, br",
			"Host": "<calculated when request is sent>",
			"Connection": "keep-alive",
			"x-auth-token": API_TOKEN
		}, timeout=5)
		print(resp.json())
	except Exception as e:
		logger.error(log_namespace + " - Error while sending data to server: " + str(e))
		check = False

	finish = time.time()
	logger.info(log_namespace + " - " + "Server send time: " + str(round(finish - start, 2)))
	return check, finish - start
	
def Loop(log_namespace):
	"""
		Description:
			Gather data and sends to API_URL
		accept:
			logging namespace for logging
		return:
			-
	"""
	while True:
		iter_start = time.time()
		check = True

		check_gather, gather_time, tvd, rst = Gather(log_namespace + ":" + "SENSORS")
		check_server, server_time = ServerRequest(log_namespace + ":" + "SERVER", tvd)
		check = check_gather and check_server

		# UpdateStat(check_gather, gather_time, rst, check_telegraf, telegraf_time, check, iter_start)

		iter_finish = time.time()
		iter_time = iter_finish - iter_start
		logger.info(log_namespace + " - " + "Loop time: " + str(round(iter_time, 2)))
		time.sleep(max(0, loop_period - iter_time))

Loop("LOOP")

