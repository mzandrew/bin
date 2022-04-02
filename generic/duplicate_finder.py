#!/usr/bin/env python3

# written 2022-03-23 by mza
# last updated 2022-04-01 by mza

# bash script version took 71m whereas this version takes 38s

import sys
import os
import stat
import re
import hashlib
import operator

upper_file_size_limit = 0
lower_file_size_limit = 0
golden = ""
chunk_size = 65536
files = []
sizes = []
total_potential_savings = 0
total_files_to_remove = 0
script_filename = "script_to_remove_all_duplicates_that_are_not_golden.sh"

# deal with early termination due to output being piped somewhere:
import signal
signal.signal(signal.SIGPIPE, signal.SIG_DFL)

def parse_arguments():
	for arg in sys.argv[1:]:
		min_max_or_golden(arg)

def make_executable(filename):
	st = os.stat(filename)
	os.chmod(filename, st.st_mode | stat.S_IEXEC)

def comma(value):
	return "{:,}".format(value)

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

def parse_human_readable_number(string):
	numeric = 0
	suffix = ""
	match = re.search("^([0-9.]+)([kKmMgGtT]*)$", string)
	if match:
		#print(match.group(1))
		numeric = float(match.group(1))
		if len(match.group())>1:
			suffix = match.group(2)
	if suffix=="k" or suffix=="K":
		numeric *= 1000
	if suffix=="m" or suffix=="M":
		numeric *= 1000000
	if suffix=="g" or suffix=="G":
		numeric *= 1000000000
	if suffix=="t" or suffix=="T":
		numeric *= 1000000000000
	return int(numeric)

def min_max_or_golden(arg):
	global upper_file_size_limit
	global lower_file_size_limit
	global golden
	if arg[0]=="+":
		upper_file_size_limit = parse_human_readable_number(arg[1:])
	elif arg[0]=="-":
		lower_file_size_limit = parse_human_readable_number(arg[1:])
	else:
		golden = arg

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
		sys.exit(1)
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
			continue
		if upper_file_size_limit:
			if upper_file_size_limit<myfile[0]:
				continue
		count += 1
		#if 0==count%250:
			#print("sorted " + str(count) + " lines")
			#print("filesize: " + str(myfile[0]))
		if last_size==myfile[0]:
			size_matches += 1
			sizes_set.add(myfile[0])
		last_size = myfile[0]
	string = "parsed " + str(count) + " total files"
	if lower_file_size_limit:
		string += " with sizes above the lower limit (" + str(lower_file_size_limit) + ")"
	if upper_file_size_limit:
		string += " and below the upper limit (" + str(upper_file_size_limit) + ")"
	print(string)
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

def uniq(input_list):
	output_list = []
	if len(input_list):
		try:
			number_of_indices = len(input_list[0])
		except:
			number_of_indices = 1
		output_list.append(input_list[0])
		for i in range(len(input_list)):
			for j in range(len(output_list)):
				match = True
				if 1<number_of_indices:
					for k in range(number_of_indices):
						if not input_list[i][k]==output_list[j][k]:
							match = False
				else:
					if not input_list[i]==output_list[j]:
						match = False
				if match:
					break
			if not match:
				output_list.append(input_list[i])
			#print(str(output_list))
	return output_list

def compare_these_size_matches(size_matches):
	global total_potential_savings
	global total_files_to_remove
	filtered_list = []
	for myfile in size_matches:
		if os.path.isfile(myfile[2]): # skip the entry if the file is gone
			filtered_list.append(myfile)
	filtered_list = uniq(filtered_list)
	if len(filtered_list)<2: # give up if there's only one left to compare
		return
	if golden=="":
		#filtered_list.sort(key=lambda x: x[1]) # sort by datestamp
		filtered_list.sort(key=operator.itemgetter(0, 2)) # sort by timestamp first, then by filename
		#filtered_list.sort(key=operator.itemgetter(2, 0)) # sort by filename first, then by timestamp
	else:
		match_count = 0
		match_list = []
		other_list = []
		for i in range(len(filtered_list)):
			match = re.search("^" + golden, filtered_list[i][2])
			if match:
				match_count += 1
				match_list.append(filtered_list[i])
				#print("match = " + filtered_list[i][2])
			else:
				other_list.append(filtered_list[i])
		if match_count==1:
			filtered_list = []
			filtered_list.extend(match_list)
			other_list.sort(key=operator.itemgetter(0, 2)) # sort by timestamp first, then by filename
			filtered_list.extend(other_list)
		elif match_count>1:
			# need to special case this and keep going if the golden files aren't identical, since there still may be other duplicates
			print("too many matches for golden string:")
			for each in match_list:
				print(each[2])
			print("")
			return
		else:
			filtered_list.sort(key=operator.itemgetter(0, 2)) # sort by timestamp first, then by filename
			#filtered_list.sort(key=operator.itemgetter(2, 0)) # sort by filename first, then by timestamp
	hashes = []
	match_string = "  "
	#remove_string = "rm -v"
	remove_string = "rm"
	match_count = 0
	for i in range(len(filtered_list)):
		try:
			myhash = hashme(filtered_list[i][2])
		except KeyboardInterrupt:
			sys.exit(2)
		except:
			continue
		matches = False
		for j in range(len(hashes)):
			if hashes[j]==myhash:
				match_string = str(j).rjust(2)
				matches = True
				match_count += 1
				total_potential_savings += filtered_list[i][0]
				total_files_to_remove += 1
				remove_string += " \"" + filtered_list[i][2]  + "\""
		if not matches:
			hashes.append(myhash)
			match_string = "  "
		print(filtered_list[i][1] + " " + str(filtered_list[i][0]).rjust(12) + " " + myhash + " " + match_string + " " + filtered_list[i][2])
	if match_count:
		print(remove_string, file=script_file)
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

def show_potential_savings():
	if total_potential_savings:
		print("")
		print("total duplicate files = " + comma(total_files_to_remove))
		print("total potential savings = " + comma(total_potential_savings) + " bytes")

with open(script_filename, "a") as script_file:
	print("#!/bin/bash -e", file=script_file)
	parse_arguments()
	read_it_in()
	find_size_matches()
	find_number_of_different_sizes()
	compare_file_hashes()
	show_potential_savings()
	print("\n", file=script_file)
make_executable(script_filename)

