# written 2022-10-29 by mza
# with help from https://learn.adafruit.com/adafruit-circuit-playground-express/circuitpython-neopixel
# and from https://learn.adafruit.com/adafruit-circuit-playground-express/circuitpython-digital-in-out
# and from https://learn.adafruit.com/circuitpython-essentials/circuitpython-neopixel
# last updated 2022-11-09 by mza

import time
import board
import neopixel
import digitalio

#brightness = 0.04
brightness = 1.0
hours = neopixel.NeoPixel(board.A3, 12, pixel_order=(1, 0, 2, 3), brightness=brightness, auto_write=False)
minutes = neopixel.NeoPixel(board.D2, 60, pixel_order=(1, 0, 2, 3), brightness=brightness, auto_write=False)
BLACK = (0, 0, 0, 0)
PURPLE = (180, 0, 255, 0)
GREEN = (0, 255, 128, 0)
BLUE = (0, 0, 255, 0)

h = 0
m = 0
while True:
	print(str(h) + ":" + str(m))
	hours.fill(BLACK)
	hours[h] = BLUE
	h += 1
	if 11<h:
		h = 0
	minutes.fill(BLACK)
	minutes[m] = BLUE
	m += 1
	if 59<m:
		m = 0
	hours.show()
	minutes.show()
	time.sleep(1)

