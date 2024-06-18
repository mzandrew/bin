#!/bin/env python3

# written 2024-06-15 by mza
# walktree following gopro.py
# with exif help from https://stackoverflow.com/a/56571871
# with pathlib help from https://stackoverflow.com/a/45353565/5728815
# last updated 2024-06-17 by mza

should_change_filename    = True	# MZA_5054.JPG -> 2023-07-09.055650.MZA_5054.JPG
quiet_mode                = False
should_lowercase_stem     = False	# MZA_5054.JPG -> mza_5054.JPG 
should_lowercase_suffix   = False	# MZA_5054.JPG -> MZA_5054.jpg 
should_change_jpg_to_jpeg = False	# MZA_5054.JPG -> MZA_5054.JPEG 
fake_it                   = False	# whether to actually rename the files (for testing)

can_process_imagefiles = False
can_process_moviefiles = False
import os, sys, stat, re, time
from pathlib import Path
try:
	from PIL import Image, ExifTags
	can_process_imagefiles = True
except:
	print("can't process imagefiles")
	print("suggest: sudo apt install -y python3-pil")
try:
	import ffmpeg
	can_process_moviefiles = True
except:
	print("can't process moviefiles")
	print("suggest: sudo apt install -y ffmpeg; pip3 install ffmpeg-python")

dirs = []
image_filenames = []
movie_filenames = []
other_filenames = []
potential_image_filenames = set()
potential_movie_filenames = set()
potential_other_filenames = set()

def walktree(dirname, function_name1, function_name2):
	#print("dirname \"" + dirname + "\" found")
	if not os.path.exists(dirname):
		print(dirname + " does not exist")
		return
	dirmode = os.stat(dirname).st_mode
	filelist = []
	if stat.S_ISDIR(dirmode):
		filelist = os.listdir(dirname)
	elif stat.S_ISREG(dirmode):
		filelist = [ dirname ]
		dirname = ""
	for filename in filelist:
		pathname = os.path.join(dirname, filename)
		if not os.path.exists(pathname):
			print("file " + pathname + " does not exist")
			continue
		mode = os.stat(pathname).st_mode
		if stat.S_ISDIR(mode):
			walktree(pathname, function_name1, function_name2)
		elif stat.S_ISREG(mode):
			matched = False
			match = re.match("^(.*)(jpg|jpeg|png|bmp|tiff|thm|gif)$", pathname, re.IGNORECASE)
			if match:
				matched = True
				function_name1(pathname)
			match = re.match("^(.*)(mp4|avi|3gp)$", pathname, re.IGNORECASE)
			if match:
				matched = True
				function_name2(pathname)
			if not matched:
				process_otherfile(pathname)
		else:
			print("found non-dir, non-regular-file " + pathname)

def process_otherfile(filename):
	resolved_filename = Path(filename).resolve()
	if resolved_filename not in potential_other_filenames:
		other_filenames.append(filename)
		potential_other_filenames.add(resolved_filename)

def process_imagefile(filename):
	#print("filename \"" + filename + "\" found")
	resolved_filename = Path(filename).resolve()
	if resolved_filename not in potential_image_filenames:
		image_filenames.append(filename)
		potential_image_filenames.add(resolved_filename)

def process_moviefile(filename):
	#print("filename \"" + filename + "\" found")
	resolved_filename = Path(filename).resolve()
	if resolved_filename not in potential_movie_filenames:
		movie_filenames.append(filename)
		potential_movie_filenames.add(resolved_filename)

def process_imagefiles():
	number_of_changed_filenames = 0
	number_of_changed_datestamps = 0
	for filename in image_filenames:
		if not os.path.exists(filename):
			print("file " + filename + " disappeared")
			continue
		#print("procesing file " + filename + "...")
		exif = Image.open(filename).getexif()
		if exif is not None:
			for key, val in exif.items():
				# example: "DateTime:2023:12:26 19:26:54"
				if "DateTime"==ExifTags.TAGS[key]:
					current_datestamp = os.path.getmtime(filename)
					#print(str(current_datestamp))
					#print(f'{ExifTags.TAGS[key]}:{val}')
					new_datestamp = time.strptime(val, "%Y:%m:%d %H:%M:%S")
					#Path(filename).touch(times=new_datestamp)
					new_datestamp_epoch = time.mktime(new_datestamp)
					new_datestamp_string = time.strftime("%Y-%m-%d+%H:%M:%S", new_datestamp)
					new_filename_datestamp_string = time.strftime("%Y-%m-%d.%H%M%S", new_datestamp)
					#print(new_datestamp_string)
					if should_change_filename:
						old = Path(filename)
						stem = str(old.stem)
						#match = re.search("([a-z][a-z][a-z]_[0-9][0-9][0-9][0-9].*)", stem, flags=re.IGNORECASE)
						match = re.search("^" + new_filename_datestamp_string + "\.(.*)$", stem, flags=re.IGNORECASE)
						if match:
							stem = match.group(1)
						#print("stem: " + stem)
						if should_lowercase_stem:
							stem = str(stem).lower()
						if 0:
							match = re.search("([a-z][a-z][a-z])_([0-9][0-9][0-9][0-9].*)", stem, flags=re.IGNORECASE)
							if match:
								#stem = match.group(2)
								stem = match.group(1) + match.group(2)
								#stem = "img" + match.group(2)
						suffix = str(old.suffix)
						if should_change_jpg_to_jpeg:
							match = re.search("\.JPG", suffix, re.IGNORECASE)
							if match:
								suffix = ".JPEG"
						if should_lowercase_suffix:
							suffix = str(suffix).lower()
						new = Path(old.parent, new_filename_datestamp_string + "." + stem + suffix)
						#print("considering " + old_filename + " and " + new_filename)
						#if not old.samefile(new): # this requires both files to exist
						if not old.resolve()==new.resolve():
							old_filename = str(old.resolve())
							new_filename = str(new.resolve())
							if not quiet_mode:
								#print("renaming " + old_filename + " -> " + new_filename)
								print("renaming " + str(old) + " -> " + str(new))
							#print(old_filename + "\n" + new_filename)
							if not fake_it:
								#old.rename(new)
								os.rename(filename, new_filename)
								#filename = new_filename
								filename = str(new)
								number_of_changed_filenames += 1
					if not current_datestamp==new_datestamp_epoch:
						if not quiet_mode:
							print("changing datestamp of file " + filename + " to " + new_datestamp_string)
						os.utime(filename, (new_datestamp_epoch, new_datestamp_epoch))
						number_of_changed_datestamps += 1
				#if key in ExifTags.TAGS:
				#	print(f'{ExifTags.TAGS[key]}:{val}')
				#else:
				#	print(f'{key}:{val}')
	if number_of_changed_datestamps:
		print("changed " + str(number_of_changed_datestamps) + " image file datestamps")
	if number_of_changed_filenames:
		print("changed " + str(number_of_changed_filenames) + " image file names")

def process_moviefiles():
	number_of_changed_filenames = 0
	number_of_changed_datestamps = 0
	for filename in movie_filenames:
		if not os.path.exists(filename):
			print("file " + filename + " disappeared")
			continue
		#print("procesing file " + filename + "...")
		vid = ffmpeg.probe(filename)
		creation_time_string = vid['streams'][2]['tags']['creation_time']
		#print(creation_time_string)
		current_datestamp = os.path.getmtime(filename)
		#print("current_datestamp: " + str(current_datestamp))
		new_datestamp = time.strptime(creation_time_string, "%Y-%m-%dT%H:%M:%S.%fZ")
		#Path(filename).touch(times=new_datestamp)
		new_datestamp_epoch = time.mktime(new_datestamp)
		new_datestamp_string = time.strftime("%Y-%m-%d+%H:%M:%S", new_datestamp)
		new_filename_datestamp_string = time.strftime("%Y-%m-%d.%H%M%S", new_datestamp)
		#print("new_datestamp_string: " + new_datestamp_string)
		if should_change_filename:
			old = Path(filename)
			stem = str(old.stem)
			#match = re.search("([a-z][a-z][a-z]_[0-9][0-9][0-9][0-9].*)", stem, flags=re.IGNORECASE)
			match = re.search("^" + new_filename_datestamp_string + "\.(.*)$", stem, flags=re.IGNORECASE)
			if match:
				stem = match.group(1)
			#print("stem: " + stem)
			if should_lowercase_stem:
				stem = str(stem).lower()
			if 0:
				match = re.search("([a-z][a-z][a-z])_([0-9][0-9][0-9][0-9].*)", stem, flags=re.IGNORECASE)
				if match:
					#stem = match.group(2)
					stem = match.group(1) + match.group(2)
					#stem = "img" + match.group(2)
			suffix = str(old.suffix)
			if should_lowercase_suffix:
				suffix = str(suffix).lower()
			new = Path(old.parent, new_filename_datestamp_string + "." + stem + suffix)
			#print("considering " + old_filename + " and " + new_filename)
			#if not old.samefile(new): # this requires both files to exist
			if not old.resolve()==new.resolve():
				old_filename = str(old.resolve())
				new_filename = str(new.resolve())
				if not quiet_mode:
					#print("renaming " + old_filename + " -> " + new_filename)
					print("renaming " + str(old) + " -> " + str(new))
				#print(old_filename + "\n" + new_filename)
				if not fake_it:
					#old.rename(new)
					os.rename(filename, new_filename)
					#filename = new_filename
					filename = str(new)
					number_of_changed_filenames += 1
		if not current_datestamp==new_datestamp_epoch:
			if not quiet_mode:
				print("changing datestamp of file " + filename + " to " + new_datestamp_string)
			os.utime(filename, (new_datestamp_epoch, new_datestamp_epoch))
			number_of_changed_datestamps += 1
	if number_of_changed_datestamps:
		print("changed " + str(number_of_changed_datestamps) + " movie file datestamps")
	if number_of_changed_filenames:
		print("changed " + str(number_of_changed_filenames) + " movie file names")

def show_otherfiles():
	print("non-movie, non-image files found:")
	for filename in other_filenames:
		print(filename)

if len(sys.argv)>1:
	for arg in sys.argv[1:]:
		walktree(arg, process_imagefile, process_moviefile)
else:
	walktree(".", process_imagefile, process_moviefile)

if can_process_imagefiles:
	if len(image_filenames):
		print("found " + str(len(image_filenames)) + " image file(s)")
		process_imagefiles()

if can_process_moviefiles:
	if len(movie_filenames):
		print("found " + str(len(movie_filenames)) + " movie file(s)")
		process_moviefiles()

if len(other_filenames):
	print("found " + str(len(other_filenames)) + " other file(s)")
	show_otherfiles()

