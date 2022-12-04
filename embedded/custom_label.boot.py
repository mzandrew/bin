#!/usr/bin/env python3

# written 2021-04-21 by mza
# last updated 2022-12-03 by mza

try:
	import storage
	storage.remount("/", readonly=False)
	m = storage.getmount("/")
	#m.label = "CUSTOM"
	#m.label = "CONTINENTAL"
	#m.label = "ELDORADO"
	#m.label = "ROOF"
	#m.label = "PYPORTAL"
	#m.label = "TITANO"
	#m.label = "MAGTAG"
	#m.label = "PLOTICLE2"
	#m.label = "INDOORHUM3"
	#m.label = "INDOOR4"
	#m.label = "LASERBOX"
	#m.label = "CLEANROOM"
	#m.label = "PARHUMTEM"
	#m.label = "PARHUMTEMS3"
	#m.label = "PARHUMTEMS2"
	#m.label = "ELSEGUNDO"
	#m.label = "roof2"
	#m.label = "LORASEND2"
	m.label = "OUTDOOR"
	try:
		import os
		os.unlink("boot.py")
	except:
		print("delete self was NOT successful")
	storage.enable_usb_drive()
	storage.remount("/", readonly=True)
except:
	print("rename was NOT successful")

