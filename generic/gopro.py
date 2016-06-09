#!/usr/bin/env python
# started 2014-12-04 by mza
# code based upon that from "the python library reference 2.7.6" (page 290)
# gopro.py version started 2016-06-01
# last updated 2016-06-02

#done: limit each dir to 2000 files (ugh...) - might only be necessary if writing to a 2GB-max-file-size partition

import os, sys, stat, re
#from stat import *

dirs = []
filenames = []

def walktree(dirname, function_name):
	#print "dirname \"" + dirname + "\" found"
	for filename in os.listdir(dirname):
		pathname = os.path.join(dirname, filename)
		mode = os.stat(pathname).st_mode
		if stat.S_ISDIR(mode):
			walktree(pathname, function_name)
		elif stat.S_ISREG(mode):
			match = re.match("^(.*)jpg$", pathname, re.IGNORECASE)
			if match:
				function_name(pathname)
#		else
#			debug("unknown file type")

def process_file(filename):
	#print "filename \"" + filename + "\" found"
	filenames.append(filename)

if len(sys.argv)>1:
	for arg in sys.argv[1:]:
		walktree(arg, process_file)
else:
	walktree(".", process_file)
print "found " + str(len(filenames)) + " files",
if len(filenames) == 0:
	sys.exit()

numbers = []
for filename in filenames:
	match = re.match(".*/G([0-9]*).JPG", filename)
	if match:
		number = int(match.group(1))
		#print str(number)
		numbers.append(number)
	#print "filename \"" + filename + "\" found"
numbers.sort()

chains = []
first = numbers[0]
previous = first - 1 # shenanigans if we started with 0...
for number in numbers:
	#print str(number),
	if number == previous + 1:
	#if number == previous + 1 or count > 2000:
		previous = number
	else:
		chains.append([first, previous])
		first = number
		previous = number
chains.append([first, numbers[len(numbers)-1]])
print "from " + str(numbers[0]) + " to " + str(numbers[len(numbers)-1]),

max_files_per_dir = 2000
print "in " + str(len(chains)) + " chains:"
for chain in chains:
	count = 0
	first, last = chain
	print "[" + str(first) + "," + str(last) + "]"
	dirname = str(first).zfill(7) + "-" + str(last).zfill(7)
	if not os.path.isdir(dirname):
		print "creating dir \"" + dirname + "\"..."
		os.mkdir(dirname)
	subdirname = ""
	total = last - first
	if total > max_files_per_dir: # might only be necessary if writing to a 2GB-max-file-size partition
		subdirname = "/" + str(first).zfill(7)
		if not os.path.isdir(dirname+subdirname):
			print "creating dir \"" + dirname + subdirname + "\"..."
			os.mkdir(dirname + subdirname)
	for filename in filenames:
		match = re.match(".*/G([0-9]*).JPG", filename)
		if match:
			number = int(match.group(1))
			#print number,
			if number >= first and number <= last:
				#print number
				count = count + 1
				if total > max_files_per_dir and count > max_files_per_dir:
					count = 0
					subdirname = "/" + str(number).zfill(7)
					if not os.path.isdir(dirname+subdirname):
						print "creating dir \"" + dirname + subdirname + "\"..."
						os.mkdir(dirname + subdirname)
				new_filename = dirname + subdirname + "/G" + str(number).zfill(7) + ".JPG"
				#print new_filename
				if filename != new_filename:
					os.rename(filename, new_filename)

