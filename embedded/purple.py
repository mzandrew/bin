# written 2022-10-29 by mza
# with help from https://learn.adafruit.com/adafruit-circuit-playground-express/circuitpython-neopixel
# and from https://learn.adafruit.com/adafruit-circuit-playground-express/circuitpython-digital-in-out

import time
import board
import neopixel
import digitalio

brightness = 0.04
pixels = neopixel.NeoPixel(board.NEOPIXEL, 10, brightness=brightness, auto_write=True)
BLACK = (0, 0, 0)
PURPLE = (180, 0, 255)
switch = digitalio.DigitalInOut(board.SLIDE_SWITCH)
switch.direction = digitalio.Direction.INPUT
switch.pull = digitalio.Pull.UP

while True:
	if switch.value:
		pixels.fill(PURPLE)
	else:
		pixels.fill(BLACK)
	time.sleep(1)

