# written 2025-11-17 by mza
# last updated 2025-11-17 by mza

import time
import board
import digitalio
import math
import generic

pin_list = [ board.D8, board.D9 ]
#A = digitalio.DigitalInOut(board.D8)
#A.direction = digitalio.Direction.OUTPUT
#B = digitalio.DigitalInOut(board.D9)
#B.direction = digitalio.Direction.OUTPUT
pwm = generic.create_pwm_ios(pin_list)

deg = 0.0
delta_t = 0.001
delta_deg = 0.1
PWM_MAX = generic.PWM_MAX
while True:
	deg += delta_deg
	rad = math.pi*deg/180.0
	duty_cycle1 = math.fabs(math.sin(rad))
	duty_cycle2 = math.fabs(math.sin(rad+math.pi/2))
	print("angle=" + str(deg) + " deg; angle=" + str(rad) + " rad; duty_cycle1=" + str(duty_cycle1) + "; duty_cycle1=" + str(int(100*duty_cycle1)) + " %; duty_cycle2=" + str(duty_cycle2) + "; duty_cycle2=" + str(int(100*duty_cycle2)) + " %")
	pwm[0].duty_cycle = int(duty_cycle1*PWM_MAX)
	pwm[1].duty_cycle = int(duty_cycle2*PWM_MAX)
	time.sleep(delta_t)

