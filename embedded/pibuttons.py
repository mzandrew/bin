#!/usr/bin/env python3

# written 2021-10-06 by mza
# last updated 2021-10-06 by mza
# for use with pibuttons PCB https://oshpark.com/shared_projects/DUR2zMFP
# with help from https://raspi.tv/2013/rpi-gpio-basics-6-using-inputs-and-outputs-together-with-rpi-gpio-pull-ups-and-pull-downs

import time
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)

def setup(buttons):
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

