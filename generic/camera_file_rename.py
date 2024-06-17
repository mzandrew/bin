#!/bin/env python3

# written 2024-06-15 by mza
# walktree following gopro.py
# with exif help from https://stackoverflow.com/a/56571871
# with pathlib help from https://stackoverflow.com/a/45353565/5728815
# last updated 2024-06-17 by mza

should_change_filename    = True  # MZA_5054.JPG -> 2023-07-09.055650.MZA_5054.JPG
quiet_mode                = True
should_lowercase_stem     = False # MZA_5054.JPG -> mza_5054.JPG 
should_lowercase_suffix   = False # MZA_5054.JPG -> MZA_5054.jpg 
should_change_jpg_to_jpeg = False # MZA_5054.JPG -> MZA_5054.JPEG 
fake_it                   = False # whether to actually rename the files (for testing)

import os, sys, stat, re, time
from PIL import Image, ExifTags
from pathlib import Path

dirs = []
image_filenames = []

def walktree(dirname, function_name1):
	#print("dirname \"" + dirname + "\" found")
	for filename in os.listdir(dirname):
		pathname = os.path.join(dirname, filename)
		mode = os.stat(pathname).st_mode
		if stat.S_ISDIR(mode):
			walktree(pathname, function_name1)
		elif stat.S_ISREG(mode):
			match = re.match("^(.*)jpg$", pathname, re.IGNORECASE)
			if match:
				function_name1(pathname)
#		else
#			debug("unknown file type")

def process_imagefile(filename):
	#print("filename \"" + filename + "\" found")
	image_filenames.append(filename)

def process_imagefiles():
	number_of_changed_filenames = 0
	number_of_changed_datestamps = 0
	for filename in image_filenames:
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
								print("renaming " + old_filename + " -> " + new_filename)
							#print(old_filename + "\n" + new_filename)
							if not fake_it:
								#old.rename(new)
								os.rename(filename, new_filename)
								filename = new_filename
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
		print("changed " + str(number_of_changed_datestamps) + " datestamps")
	if number_of_changed_filenames:
		print("changed " + str(number_of_changed_filenames) + " filenames")

if len(sys.argv)>1:
	for arg in sys.argv[1:]:
		walktree(arg, process_imagefile)
else:
	walktree(".", process_imagefile)
print("found " + str(len(image_filenames)) + " image files",)
if len(image_filenames) == 0:
	sys.exit()
process_imagefiles()

