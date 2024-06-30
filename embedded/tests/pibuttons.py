#!/usr/bin/env python3

# written 2021-10-06 by mza
# last updated 2021-10-07 by mza
# for use with pibuttons PCB https://oshpark.com/shared_projects/DUR2zMFP
# with help from https://raspi.tv/2013/rpi-gpio-basics-6-using-inputs-and-outputs-together-with-rpi-gpio-pull-ups-and-pull-downs

import time
import atexit
import subprocess
import RPi.GPIO as GPIO
ios = []

def cleanup():
#	print("cleanup")
#	for io in ios:
#		func = GPIO.gpio_function(io)
#		print(str(io) + " " + str(func))
	GPIO.cleanup()
	GPIO.setmode(GPIO.BCM)
#	for io in ios:
#		#GPIO.setup(io, GPIO.IN, pull_up_down=GPIO.PUD_OFF)
#		func = GPIO.gpio_function(io)
#		print(str(io) + " " + str(func))
	command = ["gpio", "-g", "mode", "2", "ALT0"]
	subprocess.run(command)
	command = ["gpio", "-g", "mode", "3", "ALT0"]
	subprocess.run(command)
#	for io in ios:
#		func = GPIO.gpio_function(io)
#		print(str(io) + " " + str(func))

def setup(buttons):
	global ios
	GPIO.setwarnings(False)
	GPIO.setmode(GPIO.BCM)
	for b in buttons:
#		print(str(b))
#		try:
#			GPIO.setup(b, GPIO.IN, pull_up_down=GPIO.PUD_UP)
#		except RuntimeWarning:
#			print(str(b))
		if 2==b or 3==b:
			GPIO.setup(b, GPIO.IN)
		else:
			GPIO.setup(b, GPIO.IN, pull_up_down=GPIO.PUD_UP)
	ios = buttons
	atexit.register(cleanup)

def show_buttons():
	for b in buttons:
		if GPIO.input(b):
			state = "up"
		else:
			state = "down"
		print("button " + str(b) + " is " + str(state))
	print("")

if __name__ == "__main__":
	buttons = []
	buttons.append(2) # overload with SDA
	buttons.append(3) # overload with SCL
	buttons.append(4)
	buttons.append(14)
	#setup([2, 3, 4, 14])
	setup(buttons)
	while True:
		show_buttons()
		time.sleep(1)

