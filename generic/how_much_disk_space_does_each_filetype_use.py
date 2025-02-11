#!/usr/bin/env python3

# written 2022-03-24 by mza
# based on duplicate_finder.py
# last updated 2025-02-11 by mza

should_show_average_bytes_per_file = False

import sys
import os.path
import re

files = []
extensions = []
results = []

def comma(value):
	return "{:,}".format(value)

def read_it_in():
	# with help from https://stackoverflow.com/a/45223675/5728815
	count = 0
	try:
		sys.stdin.reconfigure(encoding='iso-8859-1')
		for line in iter(sys.stdin.readline, b''):
			line = line.strip()
			if line=='':
				break
			count += 1
			match = re.search("^([^ ]+)[ ]+([^ ]+)[ ]+\\.?/?(.*)\\.([^./]+)$", line)
			if match:
				datestamp = match.group(1)
				filesize = int(match.group(2))
				name = match.group(3)
				extension = match.group(4).rstrip().lower()
				files.append([extension, filesize, datestamp, name])
			else:
				match = re.search("^([^ ]+)[ ]+([^ ]+)[ ]+\\.?/?([^./]+)$", line)
				if match:
					datestamp = match.group(1)
					filesize = int(match.group(2))
					name = match.group(3)
					extension = ""
					files.append([extension, filesize, datestamp, name])
			if 0==count%100000:
				print("read " + str(count) + " lines")
				#print(datestamp + " " + str(filesize) + " " + name + extension)
	except KeyboardInterrupt:
		sys.stdout.flush()
	print("read " + str(count) + " total lines")
	files.sort()

def find_extension_matches():
	count = 0
	extensions_set = set()
	for myfile in files:
		count += 1
		#if 0==count%250:
			#print("sorted " + str(count) + " lines")
			#print("extension: " + str(myfile[0]))
		extensions_set.add(myfile[0])
	print("parsed " + str(count) + " total files")
	#print(extensions_set)
	for extension in extensions_set:
		extensions.append(extension)
	print("there are " + str(len(extensions)) + " total unique extensions")
	extensions.sort()
#	for extension in extensions:
#		print(extension)

def sum_these_extension_matches(extension_matches):
	filtered_list = extension_matches
#	filtered_list = []
#	for myfile in extension_matches:
#		if os.path.isfile(myfile[3] + myfile[0]): # skip the entry if the file is gone
#			filtered_list.append(myfile)
	filtered_list.sort()
	sum = 0
	for i in range(len(filtered_list)):
		sum += filtered_list[i][1]
	if should_show_average_bytes_per_file:
		avg = 0
		if len(filtered_list):
			avg = int(sum / len(filtered_list))
	result = comma(sum).rjust(15) + " bytes" + " " + str(len(filtered_list)).rjust(7) + " file(s)" + " "
	if should_show_average_bytes_per_file:
		result += comma(avg).rjust(15) + " (average)bytes/file "
	result += filtered_list[0][0]
	results.append([sum, result])

def go():
	j = 0
	for extension in extensions:
		extension_matches = []
		extension_matches = [ files[x] for x in range(len(files)) if files[x][0]==extension ]
		if len(extension_matches):
			sum_these_extension_matches(extension_matches)
	results.sort()
	for result in results:
		print(result[1])

read_it_in()
find_extension_matches()
go()

