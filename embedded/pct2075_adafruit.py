#!/usr/bin/env python3

# written 2020-11-24 by mza
# last updated 2022-05-19 by mza

# from https://learn.adafruit.com/adafruit-pct2075-temperature-sensor/python-circuitpython

import time
import sys
import adafruit_pct2075 # pip3 install adafruit-circuitpython-pct2075
import board
import busio
import boxcar
from DebugInfoWarningError24 import debug, info, warning, error, debug2, debug3, set_verbosity, create_new_logfile_with_string

temperature_sensors = []

def setup_temperature_sensor(i2c, address):
	#i2c.deinit()
	global temperature_sensors
	try:
		pct = adafruit_pct2075.PCT2075(i2c, address=address)
		pct.temperature
		temperature_sensors.append(pct)
	except (KeyboardInterrupt, ReloadException):
		raise
	except:
		raise
	#print(address)
	return 1

def setup(i2c, prohibited_addresses, N):
	global header_string
	pct_list = [0x37, 0x36, 0x35, 0x2f, 0x2e, 0x2d, 0x2c, 0x2b, 0x2a, 0x29, 0x28, 0x77, 0x76, 0x75, 0x74, 0x73, 0x72, 0x71, 0x70, 0x4f, 0x4e, 0x4d, 0x4c, 0x4b, 0x4a, 0x49, 0x48]
	for unallowed in prohibited_addresses:
		i = 0
		for address in pct_list:
			if address==unallowed:
				del pct_list[i]
			i += 1
	count = 0
	found_addresses = []
	for address in pct_list:
		try:
			count += setup_temperature_sensor(i2c, address)
			found_addresses.append(address)
			if 1!=count:
				header_string += ", other" + str(count)
		except (KeyboardInterrupt, ReloadException):
			raise
		except:
			pass
	if 0==count:
		error("pct2075 not present (any i2c address)")
		#raise
	else:
		debug("found " + str(count) + " temperature sensor(s)")
	global myboxcar
	myboxcar = boxcar.boxcar(count, N, "pct2075")
	return found_addresses

header_string = ", temperature (C)"

def print_header():
	info("#time" + header_string)

def get_values():
	values = []
	for each in temperature_sensors:
		try:
			values.append(each.temperature)
		except (KeyboardInterrupt, ReloadException):
			raise
		except:
			values.append(0.)
	#print(str(values))
	#print("pct2075 len(values) = " + str(len(values)))
	myboxcar.accumulate(values)
	#myboxcar.show_accumulated_values()
	return values

def show_average_values():
	myboxcar.show_average_values()

def get_average_values():
	return myboxcar.get_average_values()

def get_previous_values():
	return myboxcar.previous_values()

def measure_string():
	global temperature
	values = get_values()
	#string = ", ".join(values)
	temperature = values.pop(0)
	string = "%.1f" % temperature
	for each in values:
		string += ", %.1f" % each
	return string

def print_compact():
	try:
		date = time.strftime("%Y-%m-%d+%X, ")
	except (KeyboardInterrupt, ReloadException):
		raise
	except:
		try:
			date = get_timestring1() + ", "
		except (KeyboardInterrupt, ReloadException):
			raise
		except:
			date = ""
	string = measure_string()
	info("%s%s" % (date, string))

def test_if_present():
	try:
		temperature_sensors[0].temperature
	except (KeyboardInterrupt, ReloadException):
		raise
	except:
		return False
	return True

if __name__ == "__main__":
	try:
		i2c = busio.I2C(board.SCL1, board.SDA1)
	except (KeyboardInterrupt, ReloadException):
		raise
	except:
		i2c = busio.I2C(board.SCL, board.SDA)
	try:
		setup(i2c, [])
	except (KeyboardInterrupt, ReloadException):
		raise
	except:
		error("no pct2075 sensors present")
		sys.exit(1)
	#create_new_logfile_with_string("pct2075")
	print_header()
	while test_if_present():
		print_compact()
		#sys.stdout.flush()
		time.sleep(1)

