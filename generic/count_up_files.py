#!/usr/bin/env python3

# written 2022-04-04 by mza
# parts taken from duplicate_finder.py
# last updated 2022-04-04 by mza

import sys
import re

root_dirs = set()
files = []
root_dir_count = {}

def read_it_in():
	# with help from https://stackoverflow.com/a/45223675/5728815
	count = 0
	try:
		for line in iter(sys.stdin.readline, b''):
			if line=='':
				break
			count += 1
			match = re.search("([^ ]+)[ ]+([^ ]+)[ ]+(.*)", line)
			if match:
				datestamp = match.group(1)
				filesize = int(match.group(2))
				name = match.group(3).rstrip()
				#match = re.search("^([^/]+)/.*$", name)
				match = re.search("^\./([^/]+)/.*$", name)
				if match:	
					root_dir = match.group(1)
				else:
					root_dir = "."
				#print(root_dir)
				root_dirs.add(root_dir)
				try:
					root_dir_count[root_dir] += 1
				except:
					root_dir_count[root_dir] = 1
				files.append([root_dir, name, filesize, datestamp])
			#if 0==count%100000:
			#	print("read " + str(count) + " lines")
	except KeyboardInterrupt:
		sys.stdout.flush()
		sys.exit(1)
	#print("read " + str(count) + " total lines")
	files.sort()

def show_files():
	for i in range(len(files)):
		print(files[i][3] + " " + str(files[i][2]).rjust(12) + " " + files[i][1])

def show_count_of_files_in_each_root_dir():
	strings = []
	for root_dir in root_dirs:
		string = str(root_dir_count[root_dir]).rjust(6) + " " + root_dir
		strings.append(string)
	strings.sort()
	for string in strings:
		print(string)

read_it_in()
#show_files()
show_count_of_files_in_each_root_dir()

