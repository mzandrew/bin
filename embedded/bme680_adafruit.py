#!/usr/bin/env python3

# written 2020-10-14 by mza
# last updated 2022-08-25 by mza

# from https://learn.adafruit.com/adafruit-bme680-humidity-temperature-barometic-pressure-voc-gas/python-circuitpython

import time
import sys
import board
import busio
import adafruit_bme680 # sudo pip3 install adafruit-circuitpython-bme680
import boxcar
from DebugInfoWarningError24 import debug, info, warning, error, debug2, debug3, set_verbosity, create_new_logfile_with_string

bme680 = []
temperature_offset = []
myboxcar = []
highest_index = 0

Pa_to_atm = 101325.0 # Pa / atm
hPa_to_atm = Pa_to_atm/100.0

def setup(i2c, N, address=0x77): # other address is 0x76
	global bme680
	global highest_index
	global temperature_offset
	global myboxcar
	bme680.append(adafruit_bme680.Adafruit_BME680_I2C(i2c, address=address, debug=False))
	# change this to match the location's pressure (hPa) at sea level
	bme680[highest_index].sea_level_pressure = 1013.25
	temperature_offset.append(0.0)
	myboxcar.append(boxcar.boxcar(5, N, "bme680"))
	highest_index += 1
	#info(str(len(bme680)))
	#info(str(len(temperature_offset)))
	#info(str(len(myboxcar)))

def print_verbose(i=0):
	info("\nTemperature: %0.1f C" % float(bme680[i].temperature + temperature_offset[i]))
	info("Gas: %d ohm" % bme680[i].gas)
	info("Humidity: %0.1f %%" % bme680[i].humidity)
	#info("Pressure: %0.3f hPa" % bme680[i].pressure)
	info("Pressure: %0.6f atm" % bme680[i].pressure/hPa_to_atm)
	info("Altitude = %0.2f meters" % bme680[i].altitude)

#header_string = ", temperature (C), humidity (%RH), pressure (hPa), altitude (m), gas (Ohm)"
header_string = ", temperature (C), humidity (%RH), pressure (atm), altitude (m), gas (Ohm)"

def print_header():
	info("#time" + header_string)

def get_values(i=0):
	try:
		#values = [ float(bme680.temperature + temperature_offset), bme680.humidity, bme680.pressure, bme680.altitude, bme680.gas ]
		values = [ float(bme680[i].temperature + temperature_offset[i]), bme680[i].humidity, bme680[i].pressure/hPa_to_atm, bme680[i].altitude, bme680[i].gas ]
	except (KeyboardInterrupt, ReloadException):
		raise
	except:
		values = [ 0., 0., 0., 0., 0 ]
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
	temp, hum, pres, alt, gas = get_values(i)
	return ", %0.1f, %0.1f, %0.6f, %0.2f, %d" % (temp, hum, pres, alt, gas)

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
		bme680[i].temperature
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
		error("bme680 not present")
		sys.exit(1)
	create_new_logfile_with_string("bme680")
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

