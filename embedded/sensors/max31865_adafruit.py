#!/usr/bin/env python3

# written 2022-08-12 by mza
# last updated 2024-07-01 by mza

import time, sys
import board, busio, digitalio
import adafruit_max31865 # for RTD
import boxcar
from DebugInfoWarningError24 import debug, info, warning, error, debug2, debug3, set_verbosity, create_new_logfile_with_string

def setup(spi, cs_pin, N):
	cs = digitalio.DigitalInOut(cs_pin)
	global sensor
	#sensor = adafruit_max31865.MAX31865(spi, cs, wires=3, rtd_nominal=100.0, ref_resistor=430.0)
	sensor = adafruit_max31865.MAX31865(spi, cs)
	global myboxcar
	myboxcar = boxcar.boxcar(2, N, "max31865")

header_string = ", temperature (C), resistance (Ohms)"

def print_header():
	info("#time" + header_string)

def get_values():
	try:
		values = [ sensor.temperature, sensor.resistance ]
	except (KeyboardInterrupt, ReloadException):
		raise
	except:
		values = [ 25., 100. ]
	myboxcar.accumulate(values)
	return values

def show_average_values():
	myboxcar.show_average_values()

def get_average_values():
	return myboxcar.get_average_values()

def get_previous_values():
	return myboxcar.previous_values()

def measure_string():
	temperature, resistance = get_values()
	return ", %0.1f, %0.1f" % (temperature, resistance)

def print_compact():
	try:
		date = time.strftime("%Y-%m-%d+%X")
	except (KeyboardInterrupt, ReloadException):
		raise
	except:
		date = ""
	string = measure_string()
	info("%s, %s" % (date, string))

def test_if_present():
	try:
		sensor.temperature
	except (KeyboardInterrupt, ReloadException):
		raise
	except:
		return False
	return True

if __name__ == "__main__":
	try:
		spi = board.SPI()
		setup(spi, board.A5, 32)
	except (KeyboardInterrupt, ReloadException):
		raise
	except:
		error("RTD not present")
		sys.exit(1)
	create_new_logfile_with_string("RTD")
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

