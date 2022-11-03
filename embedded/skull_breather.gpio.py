# written 2022-10-31 by mza
# last updated 2022-10-31 by mza

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

delta = 0.01
duty_cycle = 0.05

def cycle():
	on()
	time.sleep(delta * duty_cycle)
	off()
	time.sleep(delta * (1.0-duty_cycle))

import math
pi = 3.14159
i = 0.0
while True:
	i += 0.05
	rad = 2.0*pi*i/180.0
	duty_cycle = math.sin(rad)
	print(str(i) + " " + str(rad) + " " + str(duty_cycle))
	if duty_cycle<0.0:
		off()
		time.sleep(delta)
	else:
		cycle()

#import pwmio
#PWM_MAX = 65535
#pwm = []
#pwm.append(pwmio.PWMOut(board.D1, frequency=5000, duty_cycle=0))
#pwm.append(pwmio.PWMOut(board.D0, frequency=5000, duty_cycle=0))
#pwm.append(pwmio.PWMOut(board.SCL, frequency=5000, duty_cycle=0))
#pwm.append(pwmio.PWMOut(board.SDA, frequency=5000, duty_cycle=0))
#
#while True:
#	for i in range(100):
#		pwm[2].duty_cycle
#		time.sleep(0.01)
