#!/usr/bin/env python3

# written 2020-10-14 by mza
# based on bmr680_adafruit.py
# last updated 2022-09-13 by mza

# https://learn.adafruit.com/adafruit-am2320-temperature-humidity-i2c-sensor/python-circuitpython

import time
import sys
import board
import busio
import adafruit_am2320 # sudo pip3 install adafruit-circuitpython-am2320
import boxcar
from DebugInfoWarningError24 import debug, info, warning, error, debug2, debug3, set_verbosity, create_new_logfile_with_string

am2320 = []
myboxcar = []

def setup(i2c, N, address=0x5c):
	global am2320
	global myboxcar
	am2320.append(adafruit_am2320.AM2320(i2c, address=address))
	# change this to match the location's pressure (hPa) at sea level
	myboxcar.append(boxcar.boxcar(2, N, "am2320"))
	#info(str(len(am2320)))
	#info(str(len(myboxcar)))

def print_verbose(i=0):
	info("\nTemperature: %0.1f C" % float(am2320[i].temperature))
	info("Humidity: %0.1f %%" % am2320[i].relative_humidity)

#header_string = ", temperature (C), humidity (%RH)"
header_string = ", temperature (C), humidity (%RH)"

def print_header():
	info("#time" + header_string)

def get_values(i=0):
	try:
		#values = [ am2320.temperature, am2320.relative_humidity ]
		#values = [ am2320[i].temperature, am2320[i].relative_humidity ]
		try:
			hum = am2320[i].relative_humidity
			temp = am2320[i].temperature
		except:
			time.sleep(0.1)
			temp = am2320[i].temperature
			time.sleep(0.1)
			hum = am2320[i].relative_humidity
		values = [ temp, hum ]
	except (KeyboardInterrupt, ReloadException):
		raise
	except:
		raise
		values = [ 0., 0. ]
	#info(str(i))
	myboxcar[i].accumulate(values)
	return values

def show_average_values(i=0):
	myboxcar[i].show_average_values()

def get_average_values(i=0):
	return myboxcar[i].get_average_values()

def get_previous_values(i=0):
	return myboxcar[i].previous_values()

def measure_string(i=0):
	temp, hum = get_values(i)
	return ", %0.1f, %0.1f" % (temp, hum)

def print_compact(i=0):
	try:
		date = time.strftime("%Y-%m-%d+%X")
	except (KeyboardInterrupt, ReloadException):
		raise
	except:
		date = ""
	string = measure_string(i)
	info("%s, %s" % (date, string))

def test_if_present(i=0):
	try:
		am2320[i].temperature
	except (KeyboardInterrupt, ReloadException):
		raise
	except:
		return False
	return True

if __name__ == "__main__":
	try:
		i2c = busio.I2C(board.SCL, board.SDA)
		setup(i2c, 32)
	except (KeyboardInterrupt, ReloadException):
		raise
	except:
		error("am2320 not present")
		sys.exit(1)
	create_new_logfile_with_string("am2320")
	print_header()
	while test_if_present():
		#print_verbose()
		print_compact()
		try:
			sys.stdout.flush()
		except (KeyboardInterrupt, ReloadException):
			raise
		except:
			pass
		time.sleep(1)

