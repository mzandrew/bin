# written 2025-11-17 by mza
# last updated 2025-11-17 by mza

import time
import board
import digitalio
import math
#import generic

pin_list = [ board.D8, board.D9 ] # two kb2040 pins next to boot button

PWM_MAX = 65535
def create_pwm_ios(pin_list):
	import pwmio
	global pwm_ios
	pwm_ios = []
	for pin in pin_list:
		pwm_ios.append(pwmio.PWMOut(pin, frequency=5000, duty_cycle=PWM_MAX))
	return pwm_ios
#pwm = generic.create_pwm_ios(pin_list)
pwm = create_pwm_ios(pin_list)

deg = 0.0
delta_t = 0.001
delta_deg = 0.1
while True:
	deg += delta_deg
	rad = math.pi*deg/180.0
	duty_cycle1 = math.fabs(math.sin(rad))
	duty_cycle2 = math.fabs(math.cos(rad))
	print("angle=" + str(deg) + " deg; angle=" + str(rad) + " rad; duty_cycle1=" + str(duty_cycle1) + "; duty_cycle1=" + str(int(100*duty_cycle1)) + " %; duty_cycle2=" + str(duty_cycle2) + "; duty_cycle2=" + str(int(100*duty_cycle2)) + " %")
	pwm[0].duty_cycle = int(duty_cycle1*PWM_MAX)
	pwm[1].duty_cycle = int(duty_cycle2*PWM_MAX)
	time.sleep(delta_t)

