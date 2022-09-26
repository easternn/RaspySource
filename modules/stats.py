import json

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