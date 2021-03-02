#!/bin/env python3

# written 2021-03-02 by mza
# last updated 2021-03-02 by mza

# from https://www.raspberrypi.org/blog/picamera-pure-python-interface-for-camera-module/
# and https://stackoverflow.com/a/8858026/5728815
# and https://stackoverflow.com/a/12119043/5728815
# and B2L_common.py
# and https://picamera.readthedocs.io/en/release-1.3/recipes1.html

import picamera
import datetime
import time
import shutil
import sys

destination = "/opt/photo/timelapse"
temporary_filename = "/tmp/image.jpg"

camera = picamera.PiCamera()

def keep_settings():
	camera.iso = 100
	camera.shutter_speed = camera.exposure_speed
	camera.exposure_mode = 'off'
	#camera.exposure_mode = 'auto'
	camera.awb_mode = 'sunlight'
	#camera.awb_mode = 'off'
	#g = (165.0/64.0, 543.0/256.0)
	#camera.awb_gains = g
	camera.brightness = 50

def query():
	camera.resolution = (1920, 1080)
	camera.start_preview()
	time.sleep(2)
	print("brightness: " + str(camera.brightness))
	print("exposure_mode: " + str(camera.exposure_mode))
	print("awb_mode: " + str(camera.awb_mode))
	print("awb_gains: " + str(camera.awb_gains))
	print("shutter_speed: " + str(camera.shutter_speed))
	print("exposure_speed: " + str(camera.exposure_speed))

def take_one_picture():
	timestring = time.strftime("%Y-%m-%d.%H%M%S")
	camera.capture(temporary_filename)
	filename = destination + "/" + timestring + ".jpeg"
	shutil.move(temporary_filename, filename)
	print(filename)

def timelapse():
	while True:
		t = datetime.datetime.utcnow()
		sleeptime = 60 - (t.second + t.microsecond/1000000.0)
		time.sleep(sleeptime)
		take_one_picture()
		sys.stdout.flush()

query()
keep_settings()
camera.resolution = (3280, 2464)
take_one_picture()
#time.sleep(1)
#take_one_picture()
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


