#!/bin/env python3

# written 2024-06-15 by mza
# walktree following gopro.py
# with exif help from https://stackoverflow.com/a/56571871
# with pathlib help from https://stackoverflow.com/a/45353565/5728815
# last updated 2024-06-21 by mza

# ---------------user config--------------------

default_verbosity = 3
should_process_imagefiles = True
should_process_moviefiles = True
should_change_filename    = True	# MZA_5054.JPG -> 2023-07-09.055650.MZA_5054.JPG
should_lowercase_stem     = False	# MZA_5054.JPG -> mza_5054.JPG 
should_lowercase_suffix   = False	# MZA_5054.JPG -> MZA_5054.jpg 
should_change_jpg_to_jpeg = False	# MZA_5054.JPG -> MZA_5054.JPEG 
fake_it                   = False	# whether to actually rename the files (for testing)

ignore_file_extension_list = [ "wav", "txt", "text", "tar", "lf-r", "pto", "html", "zip", "pbm", "pnm", "lst", "du-ma1", "svg", "SLDPRT", "SLDASM", "SLDDRW", "pdf", "DS_Store", "gpx", "atx", "prj", "ini", "cfg", "xcf", "dsc", "files-list", "psp", "jbf", "stf", "cam", "info", "ps", "ai", "dxf", "odg", "eps", "dem", "shp", "meta", "dbf", "shx", "sbn", "sbx", "met", "xml", "dat", "xoj", "gps", "loc", "list", "aep", "can", "swp", "mrk", "njb" ]
ignore_files_with_no_extensions = True
ignore_dir_list = [ "@eaDir" ]

# ---------------------------------------------

can_process_imagefiles = False
can_process_moviefiles = False
import os, sys, stat, re, time
from pathlib import Path
try:
	sys.path.append(os.path.dirname(__file__) + "/../lib")
	from DebugInfoWarningError import debug, debug2, info, warning, error, set_verbosity
	set_verbosity(default_verbosity)
except:
	raise
try:
	from PIL import Image, ExifTags
	can_process_imagefiles = True
except KeyboardInterrupt:
	sys.exit(2)
except:
	warning("can't process imagefiles")
	warning("suggest: sudo apt install -y python3-pil")
try:
	import ffmpeg
	can_process_moviefiles = True
except KeyboardInterrupt:
	sys.exit(3)
except:
	warning("can't process moviefiles")
	warning("suggest: sudo apt install -y ffmpeg; pip3 install ffmpeg-python")

dirs = []
image_filenames = []
movie_filenames = []
other_filenames = []
potential_image_filenames = set()
potential_movie_filenames = set()
potential_other_filenames = set()
total_number_of_changed_datestamps = 0
total_number_of_changed_filenames = 0
total_could_not_parse_datestamp_count = 0

def walktree(dirname, function_name1, function_name2):
	#print("dirname \"" + dirname + "\" found")
	matched = False
	for pdn in ignore_dir_list:
		#match = re.search(pdn, dirname, flags=re.IGNORECASE)
		match = re.search("^" + pdn + "$", os.path.basename(dirname), flags=re.IGNORECASE)
		if match:
			matched = True
	if matched:
		return
	if not os.path.exists(dirname):
		error(dirname + " does not exist")
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
			error("file " + pathname + " does not exist")
			continue
		mode = os.stat(pathname).st_mode
		if stat.S_ISDIR(mode):
			walktree(pathname, function_name1, function_name2)
		elif stat.S_ISREG(mode):
			matched = False
			match = re.match("^(.*)\.(jpg|jpeg|png|bmp|tif|tiff|thm|gif|tga)$", pathname, re.IGNORECASE)
			if match:
				matched = True
				function_name1(pathname)
			match = re.match("^(.*)\.(mp4|avi|3gp|mov)$", pathname, re.IGNORECASE)
			if match:
				matched = True
				function_name2(pathname)
			if not matched:
				process_otherfile(pathname)
		else:
			info("found non-dir, non-regular-file " + pathname)

def process_otherfile(filename):
	resolved_filename = Path(filename).resolve()
	if resolved_filename not in potential_other_filenames:
		matched = False
		for extension in ignore_file_extension_list:
			match = re.search("\." + extension + "$", filename, flags=re.IGNORECASE)
			if match:
				matched = True
		if ignore_files_with_no_extensions:
			match = re.search("\.", os.path.basename(filename))
			if not match:
				matched = True
		if not matched:
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

def parse_creation_time_string(string, filename):
	new_datestamp = 0
	date_formats = [ "%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%d %H:%M:%S", "%Y:%m:%d %H:%M:%S", "%Y:%m:%d %H:%M:%S\x00", "%Y-%m-%d", "%Y-%m-%dT%H:%M:%S%z" ]
	for date_format in date_formats:
		try:
			new_datestamp = time.strptime(string, date_format)
			break
		except KeyboardInterrupt:
			sys.exit(4)
		except:
			pass
	if 0==new_datestamp:
		debug("can't get datestamp \"" + string + "\" for file " + filename)
	return new_datestamp

def process_imagefiles():
	number_of_changed_filenames = 0
	number_of_changed_datestamps = 0
	could_not_parse_datestamp_count = 0
	for filename in image_filenames:
		found_datestamp = False
		if not os.path.exists(filename):
			error("file " + filename + " disappeared")
			continue
		#info("procesing file " + filename + "...")
		exif = Image.open(filename).getexif()
		if exif is None:
			debug("no exif data for file " + filename)
			could_not_parse_datestamp_count += 1
		else:
			for key, val in exif.items():
				# example: "DateTime:2023:12:26 19:26:54"
				if key in ExifTags.TAGS and "DateTime"==ExifTags.TAGS[key]:
					#debug2(f'{ExifTags.TAGS[key]}:{val}')
					new_datestamp = parse_creation_time_string(val, filename)
					if 0==new_datestamp:
						could_not_parse_datestamp_count += 1
						continue
					found_datestamp = True
					current_datestamp = os.path.getmtime(filename)
					#print(str(current_datestamp))
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
							#print("renaming " + old_filename + " -> " + new_filename)
							info("renaming " + str(old) + " -> " + str(new))
							#print(old_filename + "\n" + new_filename)
							if not fake_it:
								#old.rename(new)
								os.rename(filename, new_filename)
								#filename = new_filename
								filename = str(new)
								number_of_changed_filenames += 1
					if not current_datestamp==new_datestamp_epoch:
						info("changing datestamp of file " + filename + " to " + new_datestamp_string)
						os.utime(filename, (new_datestamp_epoch, new_datestamp_epoch))
						number_of_changed_datestamps += 1
			if not found_datestamp:
				debug("couldn't find exif datestamp for file " + filename)
				could_not_parse_datestamp_count += 1
				for key, val in exif.items():
					if key in ExifTags.TAGS:
						debug2(f'{ExifTags.TAGS[key]}:{val}')
					else:
						debug2(f'{key}:{val}')
	global total_number_of_changed_datestamps, total_number_of_changed_filenames, total_could_not_parse_datestamp_count
	if number_of_changed_datestamps:
		info("changed " + str(number_of_changed_datestamps) + " image file datestamp(s)")
		total_number_of_changed_datestamps += number_of_changed_datestamps
	if number_of_changed_filenames:
		info("changed " + str(number_of_changed_filenames) + " image file name(s)")
		total_number_of_changed_filenames += number_of_changed_filenames
	if could_not_parse_datestamp_count:
		info("could not get datestamp of " + str(could_not_parse_datestamp_count) + " image file(s)")
		total_could_not_parse_datestamp_count += could_not_parse_datestamp_count

# https://stackoverflow.com/a/51379007/5728815
flattened_json = {}
def flatten_json(json, name=""):
	if type(json) is dict:
		for key in json:
			flatten_json(json[key], key)
	elif type(json) is list:
		for i in range(len(json)):
			flatten_json(json[i])
	else:
		#print(name + ":" + str(json))
		flattened_json[name] = json

def process_moviefiles():
	number_of_changed_filenames = 0
	number_of_changed_datestamps = 0
	could_not_parse_datestamp_count = 0
	for filename in movie_filenames:
		if not os.path.exists(filename):
			error("file " + filename + " disappeared")
			continue
		#print("procesing file " + filename + "...")
		global flattened_json
		flattened_json = {}
		try:
			vid = ffmpeg.probe(filename)
			flatten_json(vid)
		except KeyboardInterrupt:
			sys.exit(5)
		except:
			debug("can't probe file " + filename + " with ffmpeg")
			could_not_parse_datestamp_count += 1
			continue
		found_creation_time_string = False
		for key in flattened_json:
			match = re.search("(creation_time|date)", str(key))
			if match:
				creation_time_string = flattened_json[key]
				found_creation_time_string = True
				break
		if not found_creation_time_string:
			debug("can't find datestamp in metadata for file " + filename)
			for key in flattened_json:
				debug2(key + ":" + str(flattened_json[key]))
			could_not_parse_datestamp_count += 1
			continue
		#print(creation_time_string)
		new_datestamp = parse_creation_time_string(creation_time_string, filename)
		if 0==new_datestamp:
			could_not_parse_datestamp_count += 1
			continue
		current_datestamp = os.path.getmtime(filename)
		#print("current_datestamp: " + str(current_datestamp))
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
				#print("renaming " + old_filename + " -> " + new_filename)
				info("renaming " + str(old) + " -> " + str(new))
				#print(old_filename + "\n" + new_filename)
				if not fake_it:
					#old.rename(new)
					os.rename(filename, new_filename)
					#filename = new_filename
					filename = str(new)
					number_of_changed_filenames += 1
		if not current_datestamp==new_datestamp_epoch:
			info("changing datestamp of file " + filename + " to " + new_datestamp_string)
			os.utime(filename, (new_datestamp_epoch, new_datestamp_epoch))
			number_of_changed_datestamps += 1
	global total_number_of_changed_datestamps, total_number_of_changed_filenames, total_could_not_parse_datestamp_count
	if number_of_changed_datestamps:
		info("changed " + str(number_of_changed_datestamps) + " movie file datestamp(s)")
		total_number_of_changed_datestamps += number_of_changed_datestamps
	if number_of_changed_filenames:
		info("changed " + str(number_of_changed_filenames) + " movie file name(s)")
		total_number_of_changed_filenames += number_of_changed_filenames
	if could_not_parse_datestamp_count:
		info("could not get datestamp for " + str(could_not_parse_datestamp_count) + " movie file(s)")
		total_could_not_parse_datestamp_count += could_not_parse_datestamp_count

def show_otherfiles():
	info("non-movie, non-image files found:")
	for filename in other_filenames:
		info(filename)

if len(sys.argv)>1:
	for arg in sys.argv[1:]:
		walktree(arg, process_imagefile, process_moviefile)
else:
	walktree(".", process_imagefile, process_moviefile)

if should_process_imagefiles:
	if can_process_imagefiles:
		if len(image_filenames):
			info("found " + str(len(image_filenames)) + " image file(s)")
			process_imagefiles()

if should_process_moviefiles:
	if can_process_moviefiles:
		if len(movie_filenames):
			info("found " + str(len(movie_filenames)) + " movie file(s)")
			process_moviefiles()

if len(other_filenames):
	info("found " + str(len(other_filenames)) + " other file(s)")
	show_otherfiles()

if total_number_of_changed_datestamps:
	info("changed " + str(total_number_of_changed_datestamps) + " file datestamp(s) in total")
if total_number_of_changed_filenames:
	info("changed " + str(total_number_of_changed_filenames) + " file name(s) in total")
if total_could_not_parse_datestamp_count:
	info("could not get datestamp for " + str(total_could_not_parse_datestamp_count) + " file(s) in total")

