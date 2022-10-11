import smbus

def read_i2c(bytes):
	bus = smbus.SMBus(1)
	data = bus.read_i2c_block_data(0x08, 0x0, bytes)
	answer = ""
	for elem in data:
		if elem == 255:
			break
		answer += chr(elem)
    bus.close()
    print(answer)
    return answer