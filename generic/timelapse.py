#!/bin/env python3

# written 2021-03-02 by mza
# last updated 2021-03-04 by mza

# from https://www.raspberrypi.org/blog/picamera-pure-python-interface-for-camera-module/
# and https://stackoverflow.com/a/8858026/5728815
# and https://stackoverflow.com/a/12119043/5728815
# and B2L_common.py
# and https://picamera.readthedocs.io/en/release-1.3/recipes1.html

import gpiozero
import picamera
import datetime
import time
import shutil
import sys

liposhim = gpiozero.Button(4)

def is_battery_running_low():
	if liposhim.is_pressed:
		#print("is_pressed")
		return "1"
	else:
		#print("not so much")
		return "0"
	#sys.exit(0)

destination = "/opt/photo/timelapse"
temporary_filename = "/tmp/image.jpg"

camera = picamera.PiCamera()

def keep_settings():
	camera.iso = 100
	#take_one_picture()
	camera.shutter_speed = camera.exposure_speed
	#take_one_picture()
	camera.exposure_mode = 'off'
	#take_one_picture()
	#camera.exposure_mode = 'auto'
	camera.awb_mode = 'sunlight'
	#take_one_picture()
	#camera.awb_mode = 'off'
	#g = (861.0/256.0, 369.0/256.0)
	#camera.awb_gains = g
	camera.brightness = 50
	#take_one_picture()

def query():
	camera.resolution = (1920, 1080)
	camera.start_preview()
	time.sleep(2)
	print("iso: " + str(camera.iso))
	print("shutter_speed: " + str(camera.shutter_speed))
	print("exposure_speed: " + str(camera.exposure_speed))
	print("exposure_mode: " + str(camera.exposure_mode))
	print("awb_mode: " + str(camera.awb_mode))
	print("awb_gains: " + str(camera.awb_gains))
	print("brightness: " + str(camera.brightness))

def take_one_picture():
	timestring = time.strftime("%Y-%m-%d.%H%M%S")
	camera.capture(temporary_filename)
	filename = destination + "/" + timestring + ".jpeg"
	shutil.move(temporary_filename, filename)
	print(filename + " " + is_battery_running_low())

def timelapse():
	while True:
		t = datetime.datetime.utcnow()
		sleeptime = 60 - (t.second + t.microsecond/1000000.0)
		time.sleep(sleeptime)
		take_one_picture()
		sys.stdout.flush()
		#sync

query()
take_one_picture()
keep_settings()
#camera.resolution = (3280, 2464) # max res of old v2 camera
#camera.resolution = (4072, 3176) # total pixels - Invalid resolution requested
#camera.resolution = (4072, 3064) # effective pixels - Invalid resolution requested: PiResolution(width=4072, height=3064)
#camera.resolution = (4056, 3040) # active pixels - Failed to enable component: Out of resources
#camera.resolution = (4056, 2288) # 16:9 - Unable to enable port vc.ril.image_encode:out:0: Out of memory
camera.resolution = (4000, 2250) # out of memory
camera.resolution = (3808, 2142) # works
take_one_picture()
timelapse()

#camera.start_preview()
#camera.vflip = True
#camera.hflip = True
#camera.brightness = 60

#camera.start_recording('video.h264')
#sleep(5)
#camera.stop_recording()

#[[my_stream = io.BytesIO()
#with picamera.PiCamera() as camera:
#    camera.start_preview()
#    # Camera warm-up time
#    time.sleep(2)
#    camera.capture(my_stream, 'jpeg')


