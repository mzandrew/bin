#!/usr/bin/env python3

# written 2020-11-25 by mza
# last updated 2022-12-03 by mza

# from https://learn.adafruit.com/adafruit-ina260-current-voltage-power-sensor-breakout/python-circuitpython
# and https://github.com/mzandrew/XRM/blob/master/predator/IV.py

import time
import sys
import board
import busio
import adafruit_ina260 # sudo pip3 install adafruit-circuitpython-ina260
import boxcar
import generic
from DebugInfoWarningError24 import debug, info, warning, error, debug2, debug3, set_verbosity, create_new_logfile_with_string_embedded

default_address = 0x40

def setup(i2c, N, address=default_address):
	global ina260
	ina260 = adafruit_ina260.INA260(i2c_bus=i2c, address=address)
	global myboxcar
	myboxcar = boxcar.boxcar(3, N, "ina260")
	return address

header_string = ", current (mA), voltage (V), power (mW)"

def print_header():
	info("#time" + header_string)

def get_values():
	try:
		values = [ ina260.current, ina260.voltage, ina260.power ]
	except:
		values = [ 0., 0., 0. ]
	myboxcar.accumulate(values)
	return values

def show_average_values():
	myboxcar.show_average_values()

def get_average_values():
	return myboxcar.get_average_values()

def get_previous_values():
	return myboxcar.previous_values()

def measure_string():
	I, V, P = get_values()
	return ", %.1f, %.3f, %.1f" % (I, V, P)

def print_compact():
	#date = time.strftime("%Y-%m-%d+%X")
	string = measure_string()
	#info("%s, %s" % (date, string))
	info("%s" % (string))

def test_if_present():
	try:
		ina260.current
	except:
		return False
	return True

if __name__ == "__main__":
	try:
		#i2c = busio.I2C(board.SCL, board.SDA)
		i2c = busio.I2C(board.SCL1, board.SDA1)
		setup(i2c, 64, default_address)
	except:
		error("ina260 not present at address 0x" + generic.hex(default_address))
		sys.exit(1)
	#create_new_logfile_with_string("ina260")
	#create_new_logfile_with_string_embedded("/", "ina260")
	print_header()
	while test_if_present():
		print_compact()
		#sys.stdout.flush()
		time.sleep(1)

