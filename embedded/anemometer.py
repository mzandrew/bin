#!/usr/bin/env python3
# from https://learn.adafruit.com/pyportal-iot-weather-station/circuitpython-code
# written 2021-11-20 by mza
# last updated 2021-11-23 by mza

import time
import board
from simpleio import map_range
import busio
import analogio
import boxcar

def setup(pin, N):
	global adc
	global myboxcar
	myboxcar = boxcar.boxcar(1, N, "anemometer")
	try:
		adc = analogio.AnalogIn(pin)
		return True
	except:
		return False

def adc_to_wind_speed(val):
	voltage_val = val / 65535 * 3.3
	return map_range(voltage_val, 0.4, 2, 0, 32.4)

def get_values():
	try:
		values = [ adc_to_wind_speed(adc.value) ]
	except:
		values = [ 0. ]
	myboxcar.accumulate(values)
	return values

def show_average_values():
	myboxcar.show_average_values()

def get_average_values():
	return myboxcar.get_average_values()

def get_previous_values():
	return myboxcar.previous_values()

def measure_string():
	values = get_values()
	return ", %.1f" % values[0]

def compact_output():
	print(measure_string())

if __name__ == "__main__":
	setup(board.A0)
	while True:
		compact_output()
		time.sleep(1)

