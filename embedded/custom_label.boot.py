#!/usr/bin/env python3

# written 2021-04-21 by mza
# last updated 2022-05-13 by mza

import storage

try:
	storage.remount("/", readonly=False)
	m = storage.getmount("/")
	m.label = "CUSTOM"
	storage.remount("/", readonly=True)
	storage.enable_usb_drive()
except:
	print("rename was NOT successful")

