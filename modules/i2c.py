import smbus
import time

def read_i2c():
	sensor_data = {}
	bus = smbus.SMBus(1)
	period = 2
	now = time.time()
	while True:
		if time.time() > now + period:
			break
		try:
			data = bus.read_i2c_block_data(0x08, 0x0, 10)
			answer = ""
			if (data[0] != ord("$")):
				continue
			for elem in data[1:]:
				if elem == ord("$"):
					break
				answer += chr(elem)
			key, value = answer.split('=')
			if key == "" or value == "":
				continue
			sensor_data[key] = value
		except:
			bus.close()
			bus = smbus.SMBus(1)
		time.sleep(0.1)
	bus.close()
	print(sensor_data)
	return sensor_data

