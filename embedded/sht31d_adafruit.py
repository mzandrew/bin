#!/usr/bin/env python3

# from https://learn.adafruit.com/adafruit-sht31-d-temperature-and-humidity-sensor-breakout/python-circuitpython
# written 2021-11-21 by mza
# last updated 2022-01-12 by mza

import board
import busio
import adafruit_sht31d
import boxcar

loopcount = 0
HEATER_N = 10

def setup(i2c, N):
	global sht31d
	try:
		sht31d = adafruit_sht31d.SHT31D(i2c)
	except:
		raise
	global myboxcar
	myboxcar = boxcar.boxcar(2, N, "sht31d")
	#return adafruit_sht31d._SHT31_DEFAULT_ADDRESS
	return 0x44

def test_if_present():
	try:
		sht31d.temperature
	except:
		print("sht31d not present")
		return False
	return True

def get_values():
	try:
		values = [ sht31d.relative_humidity, sht31d.temperature ]
	except:
		values = [ 0., 0. ]
	myboxcar.accumulate(values)
	return values

def show_average_values():
	myboxcar.show_average_values()

def get_average_values():
	return myboxcar.get_average_values()

def get_previous_values():
	return myboxcar.previous_values()

def measure_string():
	global loopcount
	if 0==loopcount:
		sht31d.heater = False
	values = get_values()
	string = ", %.1f, %.1f" % (values[0], values[1])
	loopcount += 1
	if HEATER_N<=loopcount:
		loopcount = 0
		sht31d.heater = True
	return string

def compact_output():
	print(measure_string())

if __name__ == "__main__":
	i2c = busio.I2C(board.SCL, board.SDA)
	setup(i2c)
	while True:
		compact_output()
		time.sleep(1)

