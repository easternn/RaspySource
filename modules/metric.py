def MakeMetric(sensor_type, field_key, field_value, unix_timestamp):
	return {"sensorType": sensor_type,
			"fieldName": field_key,
			"value": field_value,
			"unixTimestamp": unix_timestamp}