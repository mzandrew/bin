#!/usr/bin/env python3

# written 2020-11-24 by mza
# last updated 2021-09-10 by mza

# from https://learn.adafruit.com/adafruit-pct2075-temperature-sensor/python-circuitpython

import time
import sys
import board
import busio
import adafruit_pct2075 # sudo pip3 install adafruit-circuitpython-pct2075/
from DebugInfoWarningError24 import debug, info, warning, error, debug2, debug3, set_verbosity, create_new_logfile_with_string

temperature_sensors = []

def setup_temperature_sensor(i2c, address):
	#i2c.deinit()
	global temperature_sensors
	try:
		pct = adafruit_pct2075.PCT2075(i2c, address=address)
		pct.temperature
		temperature_sensors.append(pct)
	except:
		raise
	#print(address)
	return 1

def setup(i2c):
	global header_string
	count = 0
	#for address in [0x37, 0x36, 0x35, 0x2f, 0x2e, 0x2d, 0x2c, 0x2b, 0x2a, 0x29, 0x28, 0x77, 0x76, 0x75, 0x74, 0x73, 0x72, 0x71, 0x70, 0x4f, 0x4e, 0x4d, 0x4c, 0x4b, 0x4a, 0x49, 0x48]:
	for address in [0x37, 0x36, 0x35, 0x2f, 0x2e, 0x2d, 0x2c, 0x2b, 0x2a, 0x29, 0x28, 0x76, 0x75, 0x74, 0x73, 0x72, 0x4f, 0x4e, 0x4d, 0x4c, 0x4b, 0x4a, 0x49, 0x48]: # omit 0x70 and 0x71 and 0x77
		#print(address)
		try:
			count += setup_temperature_sensor(i2c, address)
			if 1!=count:
				header_string += ", other" + str(count)
		except:
			pass
	if 0==count:
		error("pct2075 not present (any i2c address)")
	else:
		info("found " + str(count) + " temperature sensor(s)")
	return count

header_string = ", temperature (C)"

def print_header():
	info("#time" + header_string)

def measure():
	result = []
	for each in temperature_sensors:
		try:
			result.append(each.temperature)
		except:
			pass
	return result

def measure_string():
	global temperature
	result = measure()
	#string = ", ".join(result)
	temperature = result.pop(0)
	string = "%.1f" % temperature
	for each in result:
		string += ", %.1f" % each
	return string

def print_compact():
	try:
		date = time.strftime("%Y-%m-%d+%X, ")
	except:
		try:
			date = get_timestring1() + ", "
		except:
			date = ""
	string = measure_string()
	info("%s%s" % (date, string))

def test_if_present():
	try:
		temperature_sensors[0].temperature
	except:
		return False
	return True

if __name__ == "__main__":
	i2c = busio.I2C(board.SCL1, board.SDA1)
	try:
		setup(i2c)
	except:
		error("no pct2075 sensors present")
		sys.exit(1)
	#create_new_logfile_with_string("pct2075")
	print_header()
	while test_if_present():
		print_compact()
		#sys.stdout.flush()
		time.sleep(1)

