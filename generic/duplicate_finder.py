#!/usr/bin/env python3

# written 2022-03-23 by mza
# last updated 2022-03-24 by mza

#upper_file_size_limit = 0
lower_file_size_limit = 10000000
#lower_file_size_limit = 10
chunk_size = 65536

# bash script version took 71m whereas this version takes 38s

import sys
import os.path
import re
import hashlib
import operator

files = []
sizes = []

def hashme(filename):
	# with help from https://stackoverflow.com/a/59056837/5728815
	with open(filename, "rb") as f:
		file_hash = hashlib.md5() # takes 46 s
		#file_hash = hashlib.sha256() # takes 61 s
		while chunk := f.read(chunk_size):
			file_hash.update(chunk)
	#print(file_hash.digest())
	#print(file_hash.hexdigest())  # to get a printable str instead of bytes
	return file_hash.hexdigest()

def read_it_in():
	# reading in the list takes 3.6 s on a test file with 342201 lines
	# with help from https://stackoverflow.com/a/45223675/5728815
	count = 0
	try:
		for line in iter(sys.stdin.readline, b''):
			if line=='':
				break
			count += 1
			#(datestamp, filesize, name) = line.split(' ')
			#datestamp, filesize, name = re.findall("[^ ]+", line)
			# using re.search adds 2.3 s
			match = re.search("([^ ]+)[ ]+([^ ]+)[ ]+(.*)", line)
			if match:
				datestamp = match.group(1)
				filesize = int(match.group(2))
				name = match.group(3).rstrip()
				#filesize = int(filesize)
				#files.append(line) # takes an extra 0.25 s to store in a list
				files.append([filesize, datestamp, name]) # takes an extra 0.25 s to store in a list; takes an extra 1.1 s to store a list of lists
			if 0==count%100000:
				print("read " + str(count) + " lines")
				#print(re.findall("[^ ]+", line))
				#print(datestamp + " " + str(filesize) + " " + name)
			#print(line)
	except KeyboardInterrupt:
		sys.stdout.flush()
	print("read " + str(count) + " total lines")
	files.sort(reverse=True)

def find_size_matches():
	# takes 0.3 s
	count = 0
	last_size = 0
	size_matches = 0
	#for myfile in sorted(files, reverse=True):
	sizes_set = set()
	for myfile in files:
		if myfile[0]<lower_file_size_limit:
			break
		count += 1
		#if 0==count%250:
			#print("sorted " + str(count) + " lines")
			#print("filesize: " + str(myfile[0]))
		if last_size==myfile[0]:
			size_matches += 1
			sizes_set.add(myfile[0])
		last_size = myfile[0]
	print("parsed " + str(count) + " total files with sizes above the lower limit (" + str(lower_file_size_limit) + ")")
	print("found " + str(size_matches) + " total size matches")
	for size in sizes_set:
		sizes.append(size)
	sizes.sort(reverse=True)

def find_number_of_different_sizes():
	count = 0
	#for size in sorted(list(sizes), reverse=True):
	for size in sizes:
		count += 1
		#if 0==count%15:
			#print("filesize: " + str(size))
	print("found " + str(count) + " different sizes among the size matches")

def old_compare_file_hashes():
	# this adds 11.0 s
	for size in sizes:
		size_matches = [ files[x] for x in range(len(files)) if files[x][0]==size ]
		print(len(size_matches))

def compare_these_size_matches(size_matches):
	filtered_list = []
	for myfile in size_matches:
		if os.path.isfile(myfile[2]): # skip the entry if the file is gone
			filtered_list.append(myfile)
	if len(filtered_list)<2: # give up if there's only one left to compare
		return
	#filtered_list.sort(key=lambda x: x[1]) # sort by datestamp
	filtered_list.sort(key=operator.itemgetter(0, 2)) # sort by timestamp first, then by filename
	#filtered_list.sort(key=operator.itemgetter(2, 0)) # sort by filename first, then by timestamp
	hashes = []
	match_string = "  "
	for i in range(len(filtered_list)):
		try:
			myhash = hashme(filtered_list[i][2])
		except:
			continue
		matches = False
		for j in range(len(hashes)):
			if hashes[j]==myhash:
				match_string = str(j).rjust(2)
				matches = True
		if not matches:
			hashes.append(myhash)
			match_string = "  "
		print(filtered_list[i][1] + " " + str(filtered_list[i][0]).rjust(12) + " " + myhash + " " + match_string + " " + filtered_list[i][2])
	print()

def compare_file_hashes():
	j = 0
	size_matches = []
	for i in range(len(files)):
		if len(sizes)<=j:
			break
		#print(str(files[i][0]) + "," + str(sizes[j]))
		if sizes[j]<files[i][0]:
			pass
		elif files[i][0]==sizes[j]:
			size_matches.append(files[i])
		else:
			#print(len(size_matches))
			if len(size_matches):
				compare_these_size_matches(size_matches)
			size_matches = []
			j += 1
			if len(sizes)<=j:
				break
			if files[i][0]==sizes[j]:
				size_matches.append(files[i])

read_it_in()
find_size_matches()
find_number_of_different_sizes()
compare_file_hashes()

