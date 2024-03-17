#!/usr/bin/env python3

# written 2021-04-21 by mza
# last updated 2024-03-16 by mza

#desired_label = "CUSTOM"
#desired_label = "CONTINENTAL"
#desired_label = "ELDORADO"
#desired_label = "ROOF"
#desired_label = "PYPORTAL"
#desired_label = "TITANO"
#desired_label = "MAGTAG"
#desired_label = "PLOTICLE2"
#desired_label = "INDOORHUM3"
#desired_label = "INDOOR4"
#desired_label = "LASERBOX"
#desired_label = "CLEANROOM"
#desired_label = "PARHUMTEM"
#desired_label = "PARHUMTEMS3"
#desired_label = "PARHUMTEMS2"
#desired_label = "ELSEGUNDO"
#desired_label = "roof2"
#desired_label = "LORASEND2"
#desired_label = "LORASEND3"
#desired_label = "LORASEND4"
#desired_label = "7SEGCLOK"
#desired_label = "i75"
#desired_label = "neo60"
#desired_label = "neo90"
#desired_label = "neo120"
#desired_label = "neo144"
#desired_label = "neo165"
#desired_label = "CIRCUITPY"
#desired_label = "OUTDOOR"
#desired_label = "NEOCLOCK1"
#desired_label = "GEOdataLOG"
#desired_label = "LIVINGROOM"
#desired_label = "GARAGEPART"
#desired_label = "GARAGEHUM"
#desired_label = "BATHROOM"
#desired_label = "64X64CLOCK"
desired_label = "320X960CLOCK"
#desired_label = "480X320CLOCK"
#desired_label = "720X720CLOCK"

try:
	import storage
	storage.remount("/", readonly=False)
	m = storage.getmount("/")
	print(desired_label)
	if 11<len(desired_label):
		print("label too long; shortening")
		desired_label = desired_label[0:11]
	print(desired_label)
	m.label = desired_label
	try:
		import os
		os.unlink("boot.py")
	except:
		print("delete self was NOT successful")
		raise
	storage.enable_usb_drive()
	storage.remount("/", readonly=True)
except:
	print("rename was NOT successful")
	raise

