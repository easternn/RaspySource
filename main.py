source_path = '<PATH>'
import sys
sys.path.append(source_path + '/modules')

from datetime import datetime
import requests
import time
import i2c
import metric
from logger import logger

loop_period = 30
API_URL = '<API_URL>'
API_TOKEN = '<API_TOKEN>'
sensors = 
	[	{'sensorType': 'Current', 'fieldName': 'c1'}, 
		{'sensorType': 'Flow', 'fieldName': 'f1'}, 
		{'sensorType': 'Gercon', 'fieldName': 'g1'}, 
		{'sensorType': 'Temperature', 'fieldName': 't1'}, 
		{'sensorType': 'Temperature', 'fieldName': 't2'}, 
		{'sensorType': 'Temperature', 'fieldName': 't3'}, 
		{'sensorType': 'Temperature', 'fieldName': 't4'}, 
		{'sensorType': 'Temperature', 'fieldName': 't5'}, 
		{'sensorType': 'Temperature', 'fieldName': 't6'}, 
		{'sensorType': 'Temperature', 'fieldName': 't7'}, 
	]


def Gather(log_namespace):
	"""
		Description:
			Gather data from i2c
		accept:
			log_namespace - for local logging
		return:
			array of sensors in TVD format (list)
	"""
	start = time.time()

	tvd = []
	rst = {}
	mapped = {}
	check = True
	try:
		read_start = time.time()
		mapped = i2c.read_i2c()
		read_finish = time.time()
		read_unix = round((read_start + read_finish) / 2)
	except Exception as e:
		logger.error(log_namespace + " - Error while reading from i2c " + str(e))
	else:
		for sensor in sensors:
			if sensor['fieldName'] not in mapped.keys():
				logger.warning(log_namespace + " - Sensor not found: " + sensor['fieldName'])
			else:
				tvd.append(metric.MakeMetric(sensor['sensorType'], sensor['fieldName'], mapped[sensor['fieldName']], read_unix))
				
	finish = time.time()
	logger.info(log_namespace + " - " + "Gather time: " + str(round(finish - start, 2)))
	return finish - start, tvd

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

		tvd = Gather(log_namespace + ":" + "SENSORS")
		print(tvd)
		# ServerRequest(log_namespace + ":" + "SERVER", tvd)

		iter_finish = time.time()
		iter_time = iter_finish - iter_start
		logger.info(log_namespace + " - " + "Loop time: " + str(round(iter_time, 2)))
		time.sleep(max(0, loop_period - iter_time))

Loop("LOOP")

