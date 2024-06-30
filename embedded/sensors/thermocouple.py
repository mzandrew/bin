#!/usr/bin/env python3

# written 2024-06-26 by mza
# from https://learn.adafruit.com/adafruit-mcp9601/python-circuitpython
# last updated 2024-06-26 by mza

# to install:
# cp -ar adafruit_mcp9600.mpy adafruit_register* /media/mza/THERMOCOUPL/lib/
# cp -a boxcar.py DebugInfoWarningError24.py /media/mza/THERMOCOUPL/
# cp -a thermocouple.py /media/mza/THERMOCOUPL/code.py; sync

import adafruit_mcp9600
import boxcar
from DebugInfoWarningError24 import debug, info, warning, error, debug2

def setup(i2c, N=32):
	global sensor
	sensor = adafruit_mcp9600.MCP9600(i2c)
	global myboxcar
	myboxcar = boxcar.boxcar(2, N, "mcp9600")

def get_values():
	try:
		values = [ sensor.ambient_temperature, sensor.temperature ]
	except (KeyboardInterrupt, ReloadException):
		raise
	except:
		values = [ 0.0, 0.0 ]
	myboxcar.accumulate(values)
	return values

def measure_string():
	ambient, remote = get_values()
	return ", %.1f, %.1f" % (ambient, remote)

def show_average_values():
	#myboxcar.show_average_values()
	ambient, remote = get_average_values()
	print(", %.1f, %.1f" % (ambient, remote))

def get_average_values():
	return myboxcar.get_average_values()

def print_compact():
	#date = time.strftime("%Y-%m-%d+%X")
	string = measure_string()
	#info("%s, %s" % (date, string))
	info("%s" % (string))

def print_header():
	print(", ambient, remote")

if __name__ == "__main__":
	import time
	import board
	import busio
	i2c = busio.I2C(board.SCL, board.SDA, frequency=100000)
	setup(i2c, 32)
	print()
	print_header()
	i = 0
	while True:
		if 32<i:
			get_values()
			show_average_values()
		else:
			print_compact()
		i += 1
		time.sleep(1)

