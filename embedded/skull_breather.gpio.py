# written 2022-10-31 by mza
# last updated 2022-11-03 by mza

import time
import board
import digitalio

#pio1A = digitalio.DigitalInOut(board.D1)
#pio1A.direction = digitalio.Direction.OUTPUT
#pio1B = digitalio.DigitalInOut(board.D0)
#pio1B.direction = digitalio.Direction.OUTPUT
pio2A = digitalio.DigitalInOut(board.SDA)
pio2A.direction = digitalio.Direction.OUTPUT
pio2B = digitalio.DigitalInOut(board.SCL)
pio2B.direction = digitalio.Direction.OUTPUT

def off():
	pio2A.value = 1
	pio2B.value = 0

def on():
	pio2A.value = 0
	pio2B.value = 1

def cycle():
	on()
	time.sleep(delta_t * duty_cycle)
	off()
	time.sleep(delta_t * (1.0-duty_cycle))

import math
pi = 3.14159
deg = 0.0
delta_t = 0.01
delta_deg = 0.05
while True:
	deg += delta_deg
	rad = pi*deg/180.0
	duty_cycle = math.sin(rad)
	print(str(deg) + "deg " + str(rad) + "rad " + str(duty_cycle))
	if duty_cycle<0.0:
		off()
		time.sleep(delta_t)
	else:
		cycle()

