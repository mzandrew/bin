#!/usr/bin/env python3

# written 2020-10-14 by mza
# last updated 2020-11-25 by mza

# from https://learn.adafruit.com/adafruit-bme680-humidity-temperature-barometic-pressure-voc-gas/python-circuitpython

import time
import sys
import board
import busio
import adafruit_bme680 # sudo pip3 install adafruit-circuitpython-bme680

# You will usually have to add an offset to account for the temperature of
# the sensor. This is usually around 5 degrees but varies by use. Use a
# separate temperature sensor to calibrate this one.
temperature_offset = 0.0

def setup():
	i2c = busio.I2C(board.SCL, board.SDA)
	global bme680
	bme680 = adafruit_bme680.Adafruit_BME680_I2C(i2c, debug=False)
	# change this to match the location's pressure (hPa) at sea level
	bme680.sea_level_pressure = 1013.25

def print_verbose():
	print("\nTemperature: %0.1f C" % float(bme680.temperature + temperature_offset))
	print("Gas: %d ohm" % bme680.gas)
	print("Humidity: %0.1f %%" % bme680.humidity)
	print("Pressure: %0.3f hPa" % bme680.pressure)
	print("Altitude = %0.2f meters" % bme680.altitude)

header_string = ", temperature (C), humidity (%RH), pressure (hPa), altitude (m), gas (Ohm)"

def print_header():
	print("#time" + header_string)

def measure():
	return float(bme680.temperature + temperature_offset), bme680.humidity, bme680.pressure, bme680.altitude, bme680.gas

def measure_string():
	temp, hum, pres, alt, gas = measure()
	return "%0.1f, %0.1f, %0.3f, %0.2f, %d" % (temp, hum, pres, alt, gas)

def print_compact():
	date = time.strftime("%Y-%m-%d+%X")
	string = measure_string()
	print("%s, %s" % (date, string))

def test_if_present():
	try:
		bme680.temperature
	except:
		return False
	return True

if __name__ == "__main__":
	try:
		setup()
	except:
		print("bme680 not present")
		sys.exit(1)
	print_header()
	while test_if_present():
		#print_verbose()
		print_compact()
		sys.stdout.flush()
		time.sleep(1)

