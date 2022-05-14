#!/usr/bin/env python3

# written 2021-04-21 by mza
# last updated 2022-05-13 by mza

try:
	import storage
	storage.remount("/", readonly=False)
	m = storage.getmount("/")
	#m.label = "CUSTOM"
	#m.label = "CONTINENTAL"
	m.label = "ELDORADO"
	#m.label = "ROOF"
	#m.label = "PYPORTAL"
	#m.label = "TITANO"
	#m.label = "MAGTAG"
	#m.label = "PLOTICLE2"
	try:
		import os
		os.unlink("boot.py")
	except:
		print("delete self was NOT successful")
	storage.enable_usb_drive()
	storage.remount("/", readonly=True)
except:
	print("rename was NOT successful")

