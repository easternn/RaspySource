from w1thermsensor import W1ThermSensor, Sensor, Unit
from datetime import datetime
import requests
import time
import logging
import logging.config
import yaml
import json


path = '/home/pi/raspdev/'
logging_file = 'logging.yml'
stat_file = 'stat.json'
url_telegraf =  'http://localhost:8080/telegraf'
loop_period = 30

with open(path + logging_file, 'r') as logconf:
    config = yaml.load(logconf, Loader=yaml.FullLoader)

logging.config.dictConfig(config)
senslog = logging.getLogger('sensorLogger')
serlog = logging.getLogger('serverLogger')
mainlog = logging.getLogger('mainLogger')

def MakeMetric(sensor_type, field_key, field_value, unix_timestamp):
	"""
		Description: #FIXME
		accept: #FIXME
		return: #FIXME
	"""
	return {"sensor_type": sensor_type, field_key: field_value, "unix_timestamp": unix_timestamp}

def Collector_1(log_namespace, sensor_type, field_key_prefix):
	"""
		Description: #FIXME
		accept:
			log_namespace - for local logging (string)
			sensor_type - for TVD format - T (string)
			field_key_prefix - for TVD format - V (string)
		return:
			success/fail (bool)
			array of sensors in TVD format (list)
			array of read times of sensors (list)
	"""
	global senslog
	map_sensor_id = {'3c01d60797d8': 1, '3c01d6074fe9': 2, '3c01d6076aba': 3, '3c01d607ab27': 4, '3c01d607ea11': 5, '3c01d607e61b': 6,'3c01d607acf0': 7}
	
	tvd = []
	rst = {field_key_prefix + str(sensor_id_value): None for sensor_id_value in map_sensor_id.values()}
	check = True
	try:
		available_sensors = W1ThermSensor.get_available_sensors([Sensor.DS18B20])
	except Exception as e:
		senslog.error(log_namespace + " - Error while getting available sensors: " + str(e))
		check = False
	else:
		for sensor in available_sensors:
			if sensor.id not in map_sensor_id.keys():
				senslog.warning(log_namespace + " - Unknown sensor - " + str(sensor.id))
				continue
			try:
				start = time.time()
				value = sensor.get_temperature(Unit.DEGREES_C)
				finish = time.time()
			except Exception as e:
				senslog.error(log_namespace + ":" + str(map_sensor_id[sensor.id]) + " - Error while getting temperature: " + str(e))
				check = False
			else:
				avg = round((start + finish) / 2)
				tvd.append(MakeMetric(sensor_type, field_key_prefix + str(map_sensor_id[sensor.id]), value, avg))
				rst[field_key_prefix + str(map_sensor_id[sensor.id])] = finish - start
	finally:
		return (check and len(tvd) == len(map_sensor_id)), tvd, rst


def Gather(log_namespace):
	"""
		Description: #FIXME
		accept:
			log_namespace - for local loggin
		return:
			success/fail (bool)
			time of execution (float)
			array of sensors in TVD format (list)
			array of read times of sensors (list)

	"""
	global senslog
	start = time.time()

	tvd = []
	rst = {}
	check = True

	check_collector_1, tvd_collector_1, rst_collector_1 = Collector_1(log_namespace + ":" + "temp-DS18B20", "temp-DS18B20", "SENSOR_temp-DS18B20_")
	tvd += tvd_collector_1
	rst.update(rst_collector_1)
	check = check and check_collector_1

	finish = time.time()
	senslog.info(log_namespace + " - " + "Gather time: " + str(round(finish - start, 2)))
	return check, finish - start, tvd, rst

def TelegrafRequest(log_namespace, payload):
	"""
		Description: #FIXME
		accept: #FIXME
		return: #FIXME
	"""
	global serlog
	start = time.time()
	check = True

	try:
		resp = requests.post(url_telegraf, json=payload)  #FIXME
	except Exception as e:
		serlog.error(log_namespace + " - Error while sending data to telegraf: " + str(e))
		check = False

	finish = time.time()
	serlog.info(log_namespace + " - " + "Telegraf send time: " + str(round(finish - start, 2)))
	return check, finish - start

def GenerateEmptyAMSFTPObject():
	return {
		'AVG': 0,
		'MAX': 0,
		'Success': 0,
		'Fail': 0,
		'Total': 0,
		'Percentage': 0 
	}

def UpdateAMSFTPObject(obj, time_value):
	if time_value is None:
		obj['Fail'] += 1
	else:
		obj['MAX'] = max(obj['MAX'], time_value)
		obj['AVG'] = (obj['AVG'] * obj['Success'] + time_value) / (obj['Success'] + 1)
		obj['Success'] += 1
	obj['Total'] += 1
	obj['Percentage'] = round(100 * (obj['Success'] / obj['Total']), 2)

def CheckStat(stat, rst):
	if stat is None:
		stat = {}
	if 'Global' not in stat.keys() or stat['Global'] is None:
		stat['Global'] = GenerateEmptyAMSFTPObject()
	if 'Sensors' not in stat.keys() or stat['Global'] is None:
		stat['Sensors'] = GenerateEmptyAMSFTPObject()
	for sensor_id in rst.keys():
		if sensor_id not in stat.keys() or stat[sensor_id] is None:
			stat[sensor_id] = GenerateEmptyAMSFTPObject()
	if 'Telegraf' not in stat.keys() or stat['Telegraf'] is None:
		stat['Telegraf'] = GenerateEmptyAMSFTPObject()

def UpdateStat(check_gather, gather_time, rst, check_telegraf, telegraf_time, check, iter_start):
	"""
		Description: #FIXME
		accept: #FIXME
		return: #FIXME
	"""
	stat = None
	with open(path + stat_file, 'r') as f:
		stat = json.load(f)
	CheckStat(stat, rst)

	UpdateAMSFTPObject(stat['Sensors'], gather_time if check_gather else None)
	for sensor_id, time_value in rst.items():
		UpdateAMSFTPObject(stat[sensor_id], time_value)
	UpdateAMSFTPObject(stat['Telegraf'], telegraf_time if check_telegraf else None)
	UpdateAMSFTPObject(stat['Global'], time.time() - iter_start if check else None)

	with open(path + stat_file, 'w') as f:
		f.write(json.dumps(stat, indent=3))

def Loop(log_namespace):
	"""
		Description: #FIXME
		accept: #FIXME
		return: #FIXME
	"""
	global loop_period
	while True:
		iter_start = time.time()
		check = True

		check_gather, gather_time, tvd, rst = Gather(log_namespace + ":" + "SENSORS")
		check_telegraf, telegraf_time = TelegrafRequest(log_namespace + ":" + "TELEGRAF", tvd)
		check = check_gather and check_telegraf

		UpdateStat(check_gather, gather_time, rst, check_telegraf, telegraf_time, check, iter_start)

		iter_finish = time.time()
		iter_time = iter_finish - iter_start
		mainlog.info(log_namespace + " - " + "Loop time: " + str(round(iter_time, 2)))
		time.sleep(max(0, loop_period - iter_time))

Loop("LOOP")

