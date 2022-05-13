#!/usr/bin/env python3

# written 2022-05-13 by mza
# last updated 2022-05-13 by mza

try:
	import microcontroller
	microcontroller.on_next_reset(microcontroller.RunMode.UF2)
	import storage
	storage.remount("/", readonly=False)
	try:
		import os
		os.unlink("boot.py")
	except:
		print("delete self was NOT successful")
	storage.remount("/", readonly=True)
	storage.enable_usb_drive()
except:
	print("was NOT successful")

microcontroller.reset()

