#!/usr/bin/env python3

# written 2021-04-21 by mza
# last updated 2022-05-13 by mza

import storage

try:
	storage.remount("/", readonly=False)
	print("storage remount sucessful")
except:
	print("storage remount was NOT successful")

