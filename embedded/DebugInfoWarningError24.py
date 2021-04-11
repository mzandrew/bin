# written 2019-01-07 by mza to support python2.4-era SL5.11 on COPPERs
# updated 2019-03-08 to write to logfiles
# last updated 2020-12-18 by mza

import sys # stderr.write()
import time # strftime
import os # os.path.isfile() os.path.isdir() os.path.mkdir()
import atexit

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
	atexit.register(cleanup)
	info("Writing output from %s to logfile: %s" % (sys.argv[0], logfilename))

def print_string_stdout(string, should_flush=1):
	print(string)
	if should_flush:
		sys.stdout.flush()

def print_string_stderr(string, should_flush=1):
	sys.stderr.write(string + "\n")
	if should_flush:
		sys.stderr.flush()

def print_string_logfile(string, should_flush=1):
	if (logfile_is_open):
		logfile.write(string + "\n")
		if should_flush:
			logfile.flush()

def debug3(string, should_flush=1):
	if (verbosity>=6):
		string = "  DEBUG3:  " + string
		print_string_stdout(string, should_flush)
		print_string_logfile(string, should_flush)

def debug2(string, should_flush=1):
	if (verbosity>=5):
		string = "  DEBUG2:  " + string
		print_string_stdout(string, should_flush)
		print_string_logfile(string, should_flush)

def debug(string, should_flush=1):
	if (verbosity>=4):
		string = "   DEBUG:  " + string
		print_string_stdout(string, should_flush)
		print_string_logfile(string, should_flush)

def info(string, should_flush=1):
	if (verbosity>=3):
		print_string_stdout(string, should_flush)
		print_string_logfile(string, should_flush)

def warning(string, should_flush=1):
	if (verbosity>=2):
		string = " WARNING:  " + string
		print_string_stderr(string, should_flush)
		print_string_logfile(string, should_flush)

#def error(*string, level=0):
def error(string, should_flush=1):
	# from http://stackoverflow.com/questions/5574702/how-to-print-to-stderr-in-python
	if (verbosity>=1):
		string = "   ERROR:  " + string
		print_string_stderr(string, should_flush)
		print_string_logfile(string, should_flush)
#		if (level>0):
#			exit(level)

def cleanup():
	if logfile_is_open:
		logfile.close()

