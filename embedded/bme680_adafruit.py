#!/usr/bin/env python3

# from https://learn.adafruit.com/adafruit-bme680-humidity-temperature-barometic-pressure-voc-gas/python-circuitpython

import time
import board
import busio
import adafruit_bme680
import sys

# Create library object using our Bus I2C port
i2c = busio.I2C(board.SCL, board.SDA)
bme680 = adafruit_bme680.Adafruit_BME680_I2C(i2c, debug=False)
# change this to match the location's pressure (hPa) at sea level
bme680.sea_level_pressure = 1013.25
# You will usually have to add an offset to account for the temperature of
# the sensor. This is usually around 5 degrees but varies by use. Use a
# separate temperature sensor to calibrate this one.
temperature_offset = -5.0

def print_verbose():
	print("\nTemperature: %0.1f C" % float(bme680.temperature + temperature_offset))
	print("Gas: %d ohm" % bme680.gas)
	print("Humidity: %0.1f %%" % bme680.humidity)
	print("Pressure: %0.3f hPa" % bme680.pressure)
	print("Altitude = %0.2f meters" % bme680.altitude)

def print_header():
	print("#time, temperature (C), humidity (%RH), pressure (hPa), altitude (m), gas (Ohm)")

def print_compact():
	print("%s, %0.1f, %0.1f, %0.3f, %0.2f, %d" % (time.strftime("%Y-%m-%d+%X"),float(bme680.temperature + temperature_offset), bme680.humidity, bme680.pressure, bme680.altitude, bme680.gas))

print_header()
while True:
	#print_verbose()
	print_compact()
	sys.stdout.flush()
	time.sleep(1)

