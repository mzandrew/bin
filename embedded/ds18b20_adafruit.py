# https://learn.adafruit.com/using-ds18b20-temperature-sensor-with-circuitpython/circuitpython
# SPDX-FileCopyrightText: 2020 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT
# Simple demo of printing the temperature from the first found DS18x20 sensor every second.
# Author: Tony DiCola
# last updated 2021-09-19 by mza

# A 4.7Kohm pullup between DATA and POWER is REQUIRED!

import time
import board
from adafruit_onewire.bus import OneWireBus
from adafruit_ds18x20 import DS18X20

def setup(ow_bus):
	global ds18
	# Scan for sensors and grab the first one found.
	ds18 = DS18X20(ow_bus, ow_bus.scan()[0])

def test_if_present():
	try:
		ds18.temperature
	except:
		print("ds18 not present")
		return False
	return True

def measure_string():
	return ", %.1f" % ds18.temperature

def print_compact():
	print(measure_string())

# Main loop to print the temperature every second.
#while True:
#	print("Temperature: {0:0.3f}C".format(ds18.temperature))
#	time.sleep(1.0)

if __name__ == "__main__":
	# Initialize one-wire bus on board pin D5.
	ow_bus = OneWireBus(board.D5)
	setup(ow_bus)
	while test_if_present():
		print_compact()
		time.sleep(1)

