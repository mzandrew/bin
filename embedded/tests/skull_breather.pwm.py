# written 2025-11-17 by mza
# last updated 2025-11-18 by mza

import time
import board
import digitalio
import math
#import generic

#board.SPI().unlock()
board.SPI().deinit()
pin_list = [ board.D2, board.D3, board.D4, board.D5, board.D6, board.D7, board.D8, board.D9, board.A1, board.A0, board.A3, board.A2 ] # kb2040
#[ board.D10, board.MOSI, board.MISO, board.SCK ] # kb2040 pwm peripheral conflict pwm5 and pwm1 and pwm2
num_bicolor_leds = len(pin_list)//2

PWM_MAX = 65535
def create_pwm_ios(pin_list):
	import pwmio
	global pwm_ios
	pwm_ios = []
	for pin in pin_list:
		pwm_ios.append(pwmio.PWMOut(pin, frequency=5000, duty_cycle=PWM_MAX)) #ValueError: MOSI in use; RuntimeError: Internal resource(s) in use
	return pwm_ios
#pwm = generic.create_pwm_ios(pin_list)
pwm = create_pwm_ios(pin_list)

deg = 0.0
delta_t = 0.001
delta_deg = 0.1
other_delta_deg = 360.0 / num_bicolor_leds
while True:
	deg += delta_deg
	#print("angle=" + str(deg) + " deg; angle=" + str(rad) + " rad; duty_cycle1=" + str(duty_cycle1) + "; duty_cycle1=" + str(int(100*duty_cycle1)) + " %; duty_cycle2=" + str(duty_cycle2) + "; duty_cycle2=" + str(int(100*duty_cycle2)) + " %")
	for i in range(num_bicolor_leds):
		rad = math.pi*(deg+other_delta_deg*i)/180.0
		duty_cycle1 = math.fabs(math.sin(rad))
		duty_cycle2 = math.fabs(math.cos(rad))
		pwm[2*i+0].duty_cycle = int(duty_cycle1*PWM_MAX)
		pwm[2*i+1].duty_cycle = int(duty_cycle2*PWM_MAX)
	time.sleep(delta_t)

