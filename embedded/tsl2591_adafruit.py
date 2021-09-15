# https://learn.adafruit.com/adafruit-tsl2591/python-circuitpython
# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT
# Simple demo of the TSL2591 sensor.  Will print the detected light value
# every second.
# last updated 2021-09-15 by mza

import time
import board
import adafruit_tsl2591

def setup(i2c):
	global tsl2591
	tsl2591 = adafruit_tsl2591.TSL2591(i2c)
	# You can optionally change the gain and integration time:
	tsl2591.gain = adafruit_tsl2591.GAIN_LOW # (1x gain)
	# tsl2591.gain = adafruit_tsl2591.GAIN_MED # (25x gain, the default)
	# tsl2591.gain = adafruit_tsl2591.GAIN_HIGH # (428x gain)
	# tsl2591.gain = adafruit_tsl2591.GAIN_MAX # (9876x gain)
	tsl2591.integration_time = adafruit_tsl2591.INTEGRATIONTIME_100MS # (100ms, default)
	# tsl2591.integration_time = adafruit_tsl2591.INTEGRATIONTIME_200MS # (200ms)
	# tsl2591.integration_time = adafruit_tsl2591.INTEGRATIONTIME_300MS # (300ms)
	# tsl2591.integration_time = adafruit_tsl2591.INTEGRATIONTIME_400MS # (400ms)
	# tsl2591.integration_time = adafruit_tsl2591.INTEGRATIONTIME_500MS # (500ms)
	# tsl2591.integration_time = adafruit_tsl2591.INTEGRATIONTIME_600MS # (600ms)

def test_if_present():
	try:
		tsl2591.lux
	except:
		print("tsl2591 not present")
		return False
	return True

def measure_string():
	return ", %d, %d, %d, %d" % (tsl2591.lux, tsl2591.visible, tsl2591.infrared, tsl2591.full_spectrum)

def print_compact():
	print(measure_string())

# Read the total lux, IR, and visible light levels and print it every second.
#while True:
	# Read and calculate the light level in lux.
	#lux = tsl2591.lux
	#print("Total light: {0}lux".format(lux))
	# You can also read the raw infrared and visible light levels.
	# These are unsigned, the higher the number the more light of that type.
	# There are no units like lux.
	# Infrared levels range from 0-65535 (16-bit)
	#infrared = sensor.infrared
	#print("Infrared light: {0}".format(infrared))
	# Visible-only levels range from 0-2147483647 (32-bit)
	#visible = sensor.visible
	#print("Visible light: {0}".format(visible))
	# Full spectrum (visible + IR) also range from 0-2147483647 (32-bit)
	#full_spectrum = sensor.full_spectrum
	#print("Full spectrum (IR + visible) light: {0}".format(full_spectrum))
	#time.sleep(1.0)

if __name__ == "__main__":
	i2c = busio.I2C(board.SCL1, board.SDA1)
	#i2c = board.I2C()
	setup(i2c)
	while test_if_present():
		print_compact()
		time.sleep(1)

