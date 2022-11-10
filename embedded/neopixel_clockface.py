# written 2022-10-29 by mza
# with help from https://learn.adafruit.com/adafruit-circuit-playground-express/circuitpython-neopixel
# and from https://learn.adafruit.com/adafruit-circuit-playground-express/circuitpython-digital-in-out
# and from https://learn.adafruit.com/circuitpython-essentials/circuitpython-neopixel
# last updated 2022-11-09 by mza

import time
import board
import neopixel

#brightness = 0.04
brightness = 1.0
NUMBER_OF_MINUTE_PIXELS = 60
NUMBER_OF_HOUR_PIXELS = 12
#NUMBER_OF_HOUR_PIXELS = 24

MAX_HOUR = NUMBER_OF_HOUR_PIXELS - 1
hours = neopixel.NeoPixel(board.A3, NUMBER_OF_HOUR_PIXELS, pixel_order=(1, 0, 2, 3), brightness=brightness, auto_write=False)
MAX_MINUTE = NUMBER_OF_MINUTE_PIXELS - 1
minutes = neopixel.NeoPixel(board.D2, NUMBER_OF_MINUTE_PIXELS, pixel_order=(1, 0, 2, 3), brightness=brightness, auto_write=False)
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
	if MAX_HOUR<h:
		h = 0
	minutes.fill(BLACK)
	minutes[m] = BLUE
	m += 1
	if MAX_MINUTE<m:
		m = 0
	hours.show()
	minutes.show()
	#time.sleep(1/60)
	time.sleep(1)

