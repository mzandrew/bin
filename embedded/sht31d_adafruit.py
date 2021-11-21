#!/usr/bin/env python3

# from https://learn.adafruit.com/adafruit-sht31-d-temperature-and-humidity-sensor-breakout/python-circuitpython
# written 2021-11-21 by mza
# last updated 2021-11-21 by mza

import board
import busio
import adafruit_sht31d

loopcount = 0
HEATER_N = 10

def setup(i2c):
	global sensor
	try:
		sensor = adafruit_sht31d.SHT31D(i2c)
	except:
		raise
	#return adafruit_sht31d._SHT31_DEFAULT_ADDRESS
	return 0x44

def measure_string():
	global loopcount
	if 0==loopcount:
		sensor.heater = False
	string = ", " + str(sensor.relative_humidity) + ", " + str(sensor.temperature)
	loopcount += 1
	if HEATER_N<=loopcount:
		loopcount = 0
		sensor.heater = True
	return string

def compact_output():
	print(measure_string())

if __name__ == "__main__":
	i2c = busio.I2C(board.SCL, board.SDA)
	setup(i2c)
	while True:
		compact_output()
		time.sleep(1)

