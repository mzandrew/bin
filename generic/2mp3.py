#!/usr/bin/env python3

# written 2025-03-01 by mza
# walktree following gopro.py
# last updated 2025-03-01 by mza

extensions = [ "flac", "opus" ]

import os, sys, stat, re, subprocess
#from pathlib import Path
#from stat import *

dirs = []
filenames = []

def touch(file_to_change, file_to_reference):
	mtime = os.path.getmtime(file_to_reference)
	atime = os.path.getatime(file_to_reference)
	os.utime(file_to_change, (atime, mtime))

def walktree(dirname, function_name):
	#print("dirname \"" + dirname + "\" found")
	for filename in os.listdir(dirname):
		pathname = os.path.join(dirname, filename)
		mode = os.stat(pathname).st_mode
		if stat.S_ISDIR(mode):
			walktree(pathname, function_name)
		elif stat.S_ISREG(mode):
			for ext in extensions:
				match = re.match("^(.*)" + ext + "$", pathname, re.IGNORECASE)
				if match:
					function_name(pathname)
#		else
#			debug("unknown file type")

def process_file(filename):
	#print("filename \"" + filename + "\" found")
	filenames.append(filename)

if len(sys.argv)>1:
	for arg in sys.argv[1:]:
		walktree(arg, process_file)
else:
	walktree(".", process_file)
print("found " + str(len(filenames)) + " files",)
if len(filenames) == 0:
	sys.exit(0)

for file in filenames:
	#print(file)
	match = re.search("^(.*)\\.([a-zA-Z0-9]+)$", file)
	if match:
		root = match.group(1)
		ext = match.group(2)
		#print(root + " " + ext + " -> mp3")
		out = root + ".mp3"
		if not os.path.exists(out):
			subprocess.run(["lf", file])
			output = subprocess.run(["ffmpeg", "-i", file, "-ab", "320k", "-map_metadata", "0", "-id3v2_version", "3", out], capture_output=True)
			if os.path.exists(out):
				touch(out, file)
				subprocess.run(["lf", out])
				os.unlink(file)

