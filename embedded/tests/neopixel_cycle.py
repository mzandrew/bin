#!/usr/bin/env python3

# written 2021-04-21 by mza
# with help from https://learn.adafruit.com/adafruit-neopixel-driver-bff/circuitpython
# and from https://learn.adafruit.com/adafruit-qt-py-charger-bff/pinouts
# last updated 2023-12-06 by mza

# solder lipo BFF to qtpy (ensure orientation is correct): only need GND, 5V, A2 and A3

# to install:
# cp -ar adafruit_pixelbuf.mpy neopixel.mpy /media/mza/CIRCUITPY/lib/
# cp -a DebugInfoWarningError24.py boxcar.py /media/mza/NEO90/
# cp -a neopixel_cycle.py /media/mza/NEO90/code.py; sync

DELAY = 0.001
BRIGHTNESS = 0.0125
MIN_LION_VOLTAGE = 3.3
MAX_LION_VOLTAGE = 3.7
N = 60

import time
import board
from rainbowio import colorwheel
import storage
import boxcar
import analogio
import neopixel

def setup():
	global label
	label = "unknown"
	try:
		m = storage.getmount("/")
		label = m.label
	except (KeyboardInterrupt, ReloadException):
		raise
	except Exception as error_message:
		error(str(error_message))
		pass
	print("label = " + label)
	PIN = board.A3
	global numpixels
	if "NEO60"==label:
		numpixels = 60
	elif "NEO90"==label:
		numpixels = 90
	elif "NEO120"==label:
		numpixels = 120
	elif "NEO144"==label:
		numpixels = 144
	elif "NEO165"==label:
		numpixels = 165
	else:
		numpixels = 1
		PIN = board.NEOPIXEL
	print("numpixels = " + str(numpixels))
	global pixels
	pixels = neopixel.NeoPixel(PIN, numpixels, brightness=BRIGHTNESS, auto_write=False)
	global battery_monitor_pin
	battery_monitor_pin = analogio.AnalogIn(board.A2)
	global myboxcar
	myboxcar = boxcar.boxcar(1, N, "battery_percentage")

def get_battery_voltage():
	voltage = (battery_monitor_pin.value / 65535) * 6.8
	print("voltage = " + str(voltage))
	return voltage

def get_battery_percentage():
	percentage = 100.0 * (get_battery_voltage()-MIN_LION_VOLTAGE) / (MAX_LION_VOLTAGE-MIN_LION_VOLTAGE)
	if 100.0<percentage:
		percentage = 100.0
	elif percentage<0.0:
		percentage = 0.0
	print("percentage = " + str(percentage))
	return percentage

def rainbow_cycle(percentage_to_illuminate):
	if 99.9<percentage_to_illuminate:
		percentage_to_illuminate = 100.0
	last_pixel_to_illuminate = int(numpixels * percentage_to_illuminate / 100)
	print("last_pixel_to_illuminate = " + str(last_pixel_to_illuminate))
	for color in range(255):
		for pixel in range(last_pixel_to_illuminate):
			pixel_index = (pixel * 256 // numpixels) + color * 5
			pixels[pixel] = colorwheel(pixel_index & 255)
		for pixel in range(last_pixel_to_illuminate, numpixels):
			pixels[pixel] = (0, 0, 0)
		pixels.show()
		time.sleep(DELAY)

setup()
battery_percentage = get_battery_percentage()
print("initial voltage reading = " + str(battery_percentage))
i = 0
while True:
	rainbow_cycle(battery_percentage)
	myboxcar.accumulate([get_battery_percentage()])
	i += 1
	if N<i:
		battery_percentage = myboxcar.get_average_values()[0]
		print("boxcar average = " + str(battery_percentage))

