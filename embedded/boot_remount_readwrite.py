#!/usr/bin/env python3

# written 2021-04-21 by mza
# last updated 2022-05-13 by mza

import storage

try:
	m = storage.remount("/", readonly=False)
	print("storage remount (1) sucessful")
	m.label = "custom"
	try:
		storage.remount("/", readonly=True)
		print("storage remount (2) sucessful")
	except:
		print("storage remount (2) was NOT successful")
except:
	print("storage remount (1) was NOT successful")

