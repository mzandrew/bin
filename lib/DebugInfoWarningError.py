#!/usr/bin/python3
# python port of DebugInfoWarningError
# started 2015-09-16 by mza
# last updated 2025-02-03 by mza

# usage:
# from DebugInfoWarningError import debug, info, warning, error, debug2, debug3, exceptionmessage, set_verbosity, create_new_logfile_with_string
# set_verbosity(4)
# debug("some pedantic stuff here")
# info("this is an informational message")
# warning("you forgot something")
# error("you forgot something important")

import sys # stderr.write()
import time # strftime
import os # os.path.isfile() os.path.isdir() os.path.mkdir()

verbosity = 3
logfile_is_open = 0

def set_verbosity(value):
	global verbosity
	original_verbosity = verbosity
	verbosity = value
	#info(str(verbosity))
	return original_verbosity

def create_new_logfile_with_string(string):
	global logfile
	global logfile_is_open
	logdirname = "logs"
	#timestring = time.strftime("%Y-%m-%d.%H:%M:%S")
	timestring = time.strftime("%Y-%m-%d.%H%M%S")
	logfilename = logdirname + "/" + timestring + "." + string + ".log"
	if not os.path.isdir(logdirname):
		info("creating dir \"" + logdirname + "\"...")
		os.mkdir(logdirname)
	if os.path.isfile(logfilename):
		error("ERROR opening logfile %s (file already exists), exiting" % logfilename)
		sys.exit(1)
	try:
		logfile = open(logfilename, "w")
	except:
		error("ERROR opening logfile %s, exiting" % logfilename)
		sys.exit(2)
	logfile_is_open = 1
	info("Writing output from %s to logfile: %s" % (sys.argv[0], logfilename))

def print_string_stdout(string):
	print(string)
	sys.stdout.flush()

def print_string_stderr(string):
	sys.stderr.write(string + "\n")
	sys.stderr.flush()

def print_string_logfile(string):
	if (logfile_is_open):
		logfile.write(string + "\n")
		logfile.flush()

def debug3(string):
	if (verbosity>=6):
		string = "   DEBUG3:  " + string
		print_string_stdout(string)
		print_string_logfile(string)

def debug2(string):
	if (verbosity>=5):
		string = "   DEBUG2:  " + string
		print_string_stdout(string)
		print_string_logfile(string)

def debug(string):
	if (verbosity>=4):
		string = "    DEBUG:  " + string
		print_string_stdout(string)
		print_string_logfile(string)

def info(string):
	if (verbosity>=3):
		print_string_stdout(string)
		print_string_logfile(string)

def warning(string):
	if (verbosity>=2):
		string = "  WARNING:  " + string
		print_string_stderr(string)
		print_string_logfile(string)

#def error(*string, level=0):
def error(string):
	# from http://stackoverflow.com/questions/5574702/how-to-print-to-stderr-in-python
	if (verbosity>=1):
		string = "    ERROR:  " + string
		print_string_stderr(string)
		print_string_logfile(string)
#		if (level>0):
#			exit(level)

def exceptionmessage(string):
	if (verbosity>=1):
		string = "EXCEPTION:  " + string
		print_string_stderr(string)
		print_string_logfile(string)

