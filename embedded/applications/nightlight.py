# https://learn.adafruit.com/adafruit-bh1750-ambient-light-sensor?view=all
# SPDX-FileCopyrightText: 2020 Bryan Siepert, written for Adafruit Industries
# SPDX-License-Identifier: Unlicense
# based on skull-breather.pwm.py and bh1750_adafruit.py
# last updated 2026-04-20 by mza

turn_on_threshold = 400
turn_off_threshold = 600
number_of_averages = 12

import time
import board
import busio
import adafruit_bh1750
import boxcar
import digitalio
import math

PWM_MAX = 65535
deg = 0.0
delta_t = 0.001
delta_deg = 0.1

def create_pwm_ios(pin_list):
	import pwmio
	global pwm_ios
	pwm_ios = []
	for pin in pin_list:
		pwm_ios.append(pwmio.PWMOut(pin, frequency=5000, duty_cycle=PWM_MAX)) #ValueError: MOSI in use; RuntimeError: Internal resource(s) in use
	return pwm_ios

def setup(i2c, N):
	global bh1750
	bh1750 = adafruit_bh1750.BH1750(i2c)
	# https://github.com/adafruit/Adafruit_CircuitPython_BH1750/blob/main/adafruit_bh1750.py
	bh1750.resolution = adafruit_bh1750.Resolution.LOW
	#bh1750.mode = adafruit_bh1750.Mode.ONE_SHOT
	# https://www.mouser.com/datasheet/2/348/bh1750fvi-e-186247.pdf
	global myboxcar
	myboxcar = boxcar.boxcar(1, N, "bh1750")
	#return bh1750.i2c_device.device_address
	#return 0x23
	#return 0x5c
	#board.SPI().unlock()
	board.SPI().deinit()
	pin_list = [ board.D2, board.D3, board.D4, board.D5, board.D6, board.D7, board.D8, board.D9, board.A1, board.A0, board.A3, board.A2 ] # kb2040
	#[ board.D10, board.MOSI, board.MISO, board.SCK ] # kb2040 pwm peripheral conflict pwm5 and pwm1 and pwm2
	global num_bicolor_leds
	num_bicolor_leds = len(pin_list)//2
	#pwm = generic.create_pwm_ios(pin_list)
	global pwm
	pwm = create_pwm_ios(pin_list)

def test_if_present():
	try:
		bh1750.lux
	except:
		print("bh1750 not present")
		return False
	return True

def get_values():
	try:
		values = [ bh1750.lux ]
	except:
		values = [ 0. ]
	myboxcar.accumulate(values)
	return values

def show_average_values():
	myboxcar.show_average_values()

def get_average_values():
	return myboxcar.get_average_values()

def get_previous_values():
	return myboxcar.previous_values()

def measure_string():
	values = get_values()
	return ", %.1f" % values[0]

def print_compact():
	print(measure_string())

def ramp_on():
	deg = 0.0
	while deg < 90.0:
		deg += delta_deg
		for i in range(num_bicolor_leds):
			rad = math.pi*deg/180.0
			duty_cycle1 = math.fabs(math.sin(rad))
			duty_cycle2 = math.fabs(math.cos(rad))
			pwm[2*i+0].duty_cycle = int(duty_cycle1*PWM_MAX)
			pwm[2*i+1].duty_cycle = int(duty_cycle2*PWM_MAX)
		time.sleep(delta_t)

def ramp_off():
	deg = 90.0
	while 0.0 < deg:
		deg -= delta_deg
		for i in range(num_bicolor_leds):
			rad = math.pi*deg/180.0
			duty_cycle1 = math.fabs(math.sin(rad))
			duty_cycle2 = math.fabs(math.cos(rad))
			pwm[2*i+0].duty_cycle = int(duty_cycle1*PWM_MAX)
			pwm[2*i+1].duty_cycle = int(duty_cycle2*PWM_MAX)
		time.sleep(delta_t)

if __name__ == "__main__":
	#i2c = busio.I2C(board.SCL1, board.SDA1)
	i2c = board.I2C()
	setup(i2c, number_of_averages)
	state = False
	while test_if_present():
		print_compact()
		print(show_average_values())
		time.sleep(1)
		value = get_average_values()[0]
		if state and turn_off_threshold < value:
			print("just past the turn off threshold")
			ramp_off()
			state = False
		if not state and value < turn_on_threshold:
			print("just past the turn on threshold")
			ramp_on()
			state = True
		old_value = value
	import microcontroller
	microcontroller.reset()

