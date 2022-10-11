import metric
import time
from logger import logger
from w1thermsensor import W1ThermSensor, Sensor, Unit

def Collector_1(log_namespace, sensor_type, field_key_prefix):
	"""
		Description:
            Collects data from temperature sensors (DS18B20)
		accept:
			log_namespace - for local logging (string)
			sensor_type - for TVD format - T (string)
			field_key_prefix - for TVD format - V (string)
		return:
			success/fail (bool)
			array of sensors in TVD format (list)
			array of read times of sensors (list)
	"""
	map_sensor_id = {'3c01d60797d8': 1, '3c01d6074fe9': 2, '3c01d6076aba': 3, '3c01d607ab27': 4, '3c01d607ea11': 5, '3c01d607e61b': 6,'3c01d607acf0': 7}
	
	tvd = []
	rst = {field_key_prefix + str(sensor_id_value): None for sensor_id_value in map_sensor_id.values()}
	check = True
	try:
		available_sensors = W1ThermSensor.get_available_sensors([Sensor.DS18B20])
	except Exception as e:
		logger.error(log_namespace + " - Error while getting available sensors: " + str(e))
		check = False
	else:
		for sensor in available_sensors:
			if sensor.id not in map_sensor_id.keys():
				logger.warning(log_namespace + " - Unknown sensor - " + str(sensor.id))
				continue
			try:
				start = time.time()
				value = sensor.get_temperature(Unit.DEGREES_C)
				finish = time.time()
			except Exception as e:
				logger.error(log_namespace + ":" + str(map_sensor_id[sensor.id]) + " - Error while getting temperature: " + str(e))
				check = False
			else:
				avg = round((start + finish) / 2)
				tvd.append(metric.MakeMetric(sensor_type, field_key_prefix + str(map_sensor_id[sensor.id]), value, avg))
				rst[field_key_prefix + str(map_sensor_id[sensor.id])] = finish - start
	finally:
		for [key, value] in rst.items():
			if value is None:
				logger.warning(log_namespace + " - Sensor not found - " + str(key))
		return (check and len(tvd) == len(map_sensor_id)), tvd, rst