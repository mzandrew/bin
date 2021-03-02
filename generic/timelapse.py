#!/bin/env python3

# written 2021-03-02 by mza
# last updated 2021-03-02 by mza

# from https://www.raspberrypi.org/blog/picamera-pure-python-interface-for-camera-module/
# and https://stackoverflow.com/a/8858026/5728815
# and https://stackoverflow.com/a/12119043/5728815
# and B2L_common.py

import picamera
import datetime
import time
import shutil

destination = "/opt/photo/timelapse"
temporary_filename = "/tmp/image.jpg"

camera = picamera.PiCamera()

while True:
	t = datetime.datetime.utcnow()
	sleeptime = 60 - (t.second + t.microsecond/1000000.0)
	time.sleep(sleeptime)
	timestring = time.strftime("%Y-%m-%d.%H%M%S")
	camera.capture(temporary_filename)
	filename = destination + "/" + timestring + ".jpeg"
	shutil.move(temporary_filename, filename)
	print(filename)

#camera.start_preview()
#camera.vflip = True
#camera.hflip = True
#camera.brightness = 60

#camera.start_recording('video.h264')
#sleep(5)
#camera.stop_recording()

