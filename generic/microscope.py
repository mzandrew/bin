#!/usr/bin/env python3

# written 2021-03-02 by mza
# modified from timelapse.py
# last updated 2023-01-20 by mza

# from https://www.raspberrypi.org/blog/picamera-pure-python-interface-for-camera-module/
# and https://stackoverflow.com/a/8858026/5728815
# and https://stackoverflow.com/a/12119043/5728815
# and B2L_common.py
# and https://picamera.readthedocs.io/en/release-1.3/recipes1.html
# and https://projects.raspberrypi.org/en/projects/getting-started-with-picamera/7

import picamera # sudo apt install -y python3-picamera
import gpiozero
import datetime
import time
import shutil
import termios, fcntl, sys, os
import tempfile
import atexit

def remove_temporary_file_if_necessary():
	if os.path.exists(temporary_filename.name):
		os.remove(temporary_filename.name)

try:
	tilde = os.environ['HOME']
except:
	tilde = os.path.dirname(__file__) + "/../../.."
#destination = "/opt/photo/microscope"
#destination = "/opt/data/pictures/microscope"
destination = tilde + "/microscope"
print("destination: " + destination)
destination = os.path.realpath(destination)
print("destination: " + destination)
temporary_filename = tempfile.NamedTemporaryFile(prefix="image", suffix=".jpg", dir="/tmp", delete=False)
print("temporary_filename: " + temporary_filename.name)
#temporary_filename = os.mktemp(temporary_filename)
#print("temporary_filename: " + temporary_filename)
atexit.register(remove_temporary_file_if_necessary)

upper_left_button  = gpiozero.Button(2, pull_up=True)
lower_left_button  = gpiozero.Button(14, pull_up=True)
upper_right_button = gpiozero.Button(3,  pull_up=True)
lower_right_button = gpiozero.Button(4,  pull_up=True)

def fix_terminal():
	try:
		termios.tcsetattr(fd, termios.TCSAFLUSH, attrs_save)
		fcntl.fcntl(fd, fcntl.F_SETFL, flags_save)
	except:
		pass

def fix_terminal_and_quit():
	fix_terminal()
	sys.exit(0)

# from https://stackoverflow.com/a/6599441/5728815
def read_single_keypress():
	"""Waits for a single keypress on stdin.
	This is a silly function to call if you need to do it a lot because it has
	to store stdin's current setup, setup stdin for reading single keystrokes
	then read the single keystroke then revert stdin back after reading the
	keystroke.
	Returns a tuple of characters of the key that was pressed - on Linux, 
	pressing keys like up arrow results in a sequence of characters. Returns 
	('\x03',) on KeyboardInterrupt which can happen when a signal gets
	handled.
	"""
	global fd
	fd = sys.stdin.fileno()
	# save old state
	global flags_save
	flags_save = fcntl.fcntl(fd, fcntl.F_GETFL)
	global attrs_save
	attrs_save = termios.tcgetattr(fd)
	# make raw - the way to do this comes from the termios(3) man page.
	attrs = list(attrs_save) # copy the stored version to update
	# iflag
	attrs[0] &= ~(termios.IGNBRK | termios.BRKINT | termios.PARMRK
				  | termios.ISTRIP | termios.INLCR | termios. IGNCR
				  | termios.ICRNL | termios.IXON )
	# oflag
	attrs[1] &= ~termios.OPOST
	# cflag
	attrs[2] &= ~(termios.CSIZE | termios. PARENB)
	attrs[2] |= termios.CS8
	# lflag
	attrs[3] &= ~(termios.ECHONL | termios.ECHO | termios.ICANON
				  | termios.ISIG | termios.IEXTEN)
	termios.tcsetattr(fd, termios.TCSANOW, attrs)
	# turn off non-blocking
	fcntl.fcntl(fd, fcntl.F_SETFL, flags_save & ~os.O_NONBLOCK)
	# read a single keystroke
	ret = []
	try:
		ret.append(sys.stdin.read(1)) # returns a single character
		fcntl.fcntl(fd, fcntl.F_SETFL, flags_save | os.O_NONBLOCK)
		c = sys.stdin.read(1) # returns a single character
		while len(c) > 0:
			ret.append(c)
			c = sys.stdin.read(1)
	except KeyboardInterrupt:
		ret.append('\x03')
	finally:
		# restore old state
		fix_terminal()
	return tuple(ret)

def take_one_picture():
	timestring = time.strftime("%Y-%m-%d.%H%M%S")
	camera.capture(temporary_filename.name)
	filename = destination + "/" + timestring + ".jpeg"
	shutil.copy(temporary_filename.name, filename)
	#print(filename + " " + is_battery_running_low())
	print(filename)

def take_one_picture_and_crlf():
	print("\r")
	take_one_picture()
	print("\r")

use_regular_keyboard = True
try:
	termios.tcgetattr(sys.stdin.fileno())
except:
	use_regular_keyboard = False

print("press x or q to exit; any other key to take a(nother) pic")
sys.stdout.flush()
time.sleep(1)
upper_right_button.when_pressed = take_one_picture_and_crlf
lower_right_button.when_pressed = take_one_picture_and_crlf
upper_left_button.when_pressed = fix_terminal_and_quit
lower_left_button.when_pressed = fix_terminal_and_quit
try:
	#print("trying camera instatntiation")
	camera = picamera.PiCamera()
	#print("finished camera instatntiation")
	camera.awb_mode = "fluorescent"
	camera.rotation = 180
	camera.framerate = 10
	#camera.resolution = (3280, 2464) # max res of old v2 camera
	#camera.resolution = (4072, 3176) # total pixels - Invalid resolution requested
	#camera.resolution = (4072, 3064) # effective pixels - Invalid resolution requested: PiResolution(width=4072, height=3064)
	#camera.resolution = (4056, 3040) # active pixels - Failed to enable component: Out of resources
	#camera.resolution = (4056, 2288) # 16:9 - Unable to enable port vc.ril.image_encode:out:0: Out of memory
	camera.resolution = (3808, 2142) # 16:9 works but the preview blinks
	#camera.resolution = (3808, 2856) # 4:3 out of resources
	#camera.resolution = (1920, 1080) # works great
	print("starting preview...")
	camera.start_preview(resolution = (1920, 1080), alpha = 200)
	time.sleep(2)
except:
	print("try changing gpu_mem from 128 to 192 in /boot/config.txt (or from raspi-config)")
	print("if that fails, try unplugging/replugging camera cable at both ends")
	sys.exit(1)
#take_one_picture()
while True:
	if use_regular_keyboard:
		keys = read_single_keypress()
		#print(keys)
		for key in keys:
			if key=='x' or key=='q':
				sys.exit(0)
		take_one_picture()
	else:
		time.sleep(0.1)

