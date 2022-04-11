#!/usr/bin/env python3

# written 2022-03-23 by mza
# last updated 2022-04-11 by mza

# usage:
# takes a stdin pipe that consists of file listing data in the following "lf-r" format:
# 2022-02-22+13:21      3034824 ./libraries/usr.pd9
# [-nkKmMgGtT] minimum size files to consider
# [+nkKmMgGtT] maximum size files to consider
# all other arguments are interpreted as "golden" prefixes (string must match
# the first part of the input filenames exactly) and will cause the script to
# avoid recommending deletion for anything that matches
# outputs a script called "script_to_remove_all_duplicates_that_are_not_golden.sh" that should be inspected and then run

# usage examples:
# lf | duplicate_finder.py
# cat lf-r | duplicate_finder.py
# cat lf-r | duplicate_finder.py -1M +10M
# cat lf-r | grep tar$ | duplicate_finder.py
# lf ./mostly-good-stuff ./probably-duplicates | duplicate_finder.py ./mostly-good-stuff 

script_filename = "script_to_remove_all_duplicates_that_are_not_golden.sh"
potential_duplicates_filename = "potential-duplicates.lf-r-with-hashes"

import sys
import os
import stat
import re
import hashlib
import operator
import shlex

upper_file_size_limit = 0
lower_file_size_limit = 0
golden = []
chunk_size = 65536
files = []
sizes = []
total_potential_savings = 0
total_files_to_remove = 0
MAX_COMMAND_LENGTH_SOFT = 1000

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
		golden.append(arg)

def read_it_in():
	# with help from https://stackoverflow.com/a/45223675/5728815
	count = 0
	try:
		for line in iter(sys.stdin.readline, b''):
			if line=='':
				break
			count += 1
			#(datestamp, filesize, name) = line.split(' ')
			#datestamp, filesize, name = re.findall("[^ ]+", line)
			match = re.search("([^ ]+)[ ]+([^ ]+)[ ]+(.*)", line)
			if match:
				datestamp = match.group(1)
				filesize = int(match.group(2))
				name = match.group(3).rstrip()
				#filesize = int(filesize)
				files.append([filesize, datestamp, name])
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
	print("found " + str(size_matches) + " total potential duplicates")
	for size in sizes_set:
		sizes.append(size)
	sizes.sort(reverse=True)

def find_number_of_different_sizes():
	count = 0
	for size in sizes:
		count += 1
		#if 0==count%15:
			#print("filesize: " + str(size))
	print("found " + str(count) + " different sizes among the potential duplicates")
	print("")

def old_compare_file_hashes():
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

def properly_escape_this_for_the_shell(input_string):
	# https://stackoverflow.com/a/28120935/5728815
	output_string = shlex.quote(input_string)
	#print(input_string)
	#print(output_string)
	return output_string

def compare_these_size_matches(size_matches):
	global total_potential_savings
	global total_files_to_remove
	filtered_list = []
	match_list = []
	other_list = []
	for myfile in size_matches:
		if os.path.isfile(myfile[2]): # skip the entry if the file is gone
			filtered_list.append(myfile)
	filtered_list = uniq(filtered_list)
	if len(filtered_list)<2: # give up if there's only one left to compare
		return
	if 0==len(golden):
		#filtered_list.sort(key=lambda x: x[1]) # sort by datestamp
		filtered_list.sort(key=operator.itemgetter(0, 2)) # sort by timestamp first, then by filename
		#filtered_list.sort(key=operator.itemgetter(2, 0)) # sort by filename first, then by timestamp
	else:
		match_count = 0
		for i in range(len(filtered_list)):
			#print(str(i))
			immediate_match = False
			for j in range(len(golden)):
				match = re.search("^" + golden[j], filtered_list[i][2])
				if match:
					match_count += 1
					immediate_match = True
					match_list.append(filtered_list[i])
					#print("match=" + filtered_list[i][2] + "  golden_string=" + golden[j])
					break
			if not immediate_match:
				#print("other=" + filtered_list[i][2])
				other_list.append(filtered_list[i])
		other_list.sort(key=operator.itemgetter(0, 2)) # sort by timestamp first, then by filename
		#print(str(len(match_list)))
		#print(str(len(other_list)))
		if 0==len(other_list): # give up if there's none left to remove
			return
		if match_count==1:
			filtered_list = []
			#print(str(match_list))
			filtered_list.extend(match_list)
			#print(str(other_list))
			filtered_list.extend(other_list)
			#print(str(filtered_list))
		elif match_count>1:
			match_list.sort(key=operator.itemgetter(0, 2)) # sort by timestamp first, then by filename
			filtered_list = []
			filtered_list.extend(match_list)
			filtered_list.extend(other_list)
		else:
			filtered_list.sort(key=operator.itemgetter(0, 2)) # sort by timestamp first, then by filename
			#filtered_list.sort(key=operator.itemgetter(2, 0)) # sort by filename first, then by timestamp
	#print(str(len(filtered_list)))
	hashes = []
	match_string = "  "
	#remove_string_prefix = "rm -v"
	remove_string_prefix = "rm -f"
	remove_string = remove_string_prefix
	items = {}
	for i in range(len(filtered_list)):
		#print(str(i))
		try:
			myhash = hashme(filtered_list[i][2])
		except KeyboardInterrupt:
			sys.exit(2)
		except:
			continue
		matches = False
		this_one_is_brand_new = False
		for j in range(len(hashes)):
			if hashes[j]==myhash:
				match_string = str(j).rjust(2)
				matches = True
				if len(match_list)<=i:
					total_potential_savings += filtered_list[i][0]
					total_files_to_remove += 1
					remove_string += " " + properly_escape_this_for_the_shell(filtered_list[i][2])
					if MAX_COMMAND_LENGTH_SOFT<len(remove_string):
						print(remove_string, file=script_file)
						remove_string = remove_string_prefix
		if not matches:
			hashes.append(myhash)
			match_string = "  "
			this_one_is_brand_new = True
			items[myhash] = []
		string = filtered_list[i][1] + " " + str(filtered_list[i][0]).rjust(12) + " " + myhash + " " + match_string + " " + filtered_list[i][2]
		print(string)
		if this_one_is_brand_new or matches:
			items[myhash].append(string)
	if len(remove_string_prefix)<len(remove_string):
		print(remove_string, file=script_file)
	for key in items.keys():
		if 1<len(items[key]):
			for string in items[key]:
				print(string, file=potential_duplicates_file)
	print()

def compare_file_hashes():
	j = 0
	size_matches = []
	for i in range(len(files)):
		#print("i,j:" + str(i) + "," + str(j))
		if len(sizes)<=j:
			#print("got to the end of the sizes list")
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
				#print("got to the end of the sizes list")
				break
			if files[i][0]==sizes[j]:
				size_matches.append(files[i])
	if len(size_matches):
		compare_these_size_matches(size_matches)

def show_potential_savings():
	if total_files_to_remove:
		print("")
		print("total duplicate files = " + comma(total_files_to_remove))
		print("total potential savings = " + comma(total_potential_savings) + " bytes")
		print("", file=script_file)
		print("# total duplicate files = " + comma(total_files_to_remove), file=script_file)
		print("# total potential savings = " + comma(total_potential_savings) + " bytes", file=script_file)

def write_out_list_of_files_that_still_need_to_be_dealt_with(mylist):
	for each in mylist:
		string = each[1] + " " + str(each[0]).rjust(12) + " " + each[2]
		print(string, file=still_need_to_deal_with_these_file)

with open(script_filename, "a") as script_file:
	print("#!/bin/bash -e", file=script_file)
	make_executable(script_filename)
	parse_arguments()
	read_it_in()
	find_size_matches()
	find_number_of_different_sizes()
	with open(potential_duplicates_filename, "a") as potential_duplicates_file:
		compare_file_hashes()
	show_potential_savings()
	print("", file=script_file)

