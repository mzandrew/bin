#!/usr/bin/env python3
# from https://learn.adafruit.com/pyportal-iot-weather-station/circuitpython-code
# written 2021-11-20 by mza
# last updated 2021-11-20 by mza

import time
import board
from simpleio import map_range
import busio
import analogio

def setup(pin=board.A0):
	global adc
	try:
		adc = analogio.AnalogIn(pin)
		return True
	except:
		return False

def adc_to_wind_speed(val):
	voltage_val = val / 65535 * 3.3
	return map_range(voltage_val, 0.4, 2, 0, 32.4)

def measure_string():
	wind_speed = adc_to_wind_speed(adc.value)
	return ", " + str(wind_speed)

def compact_output():
	print(measure_string())

if __name__ == "__main__":
	setup(board.A0)
	while True:
		compact_output()
		time.sleep(1)

