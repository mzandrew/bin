# written 2019-01-07 by mza to support python2.4-era SL5.11 on COPPERs
# updated 2019-03-08 to write to logfiles
# last updated 2021-04-28 by mza

import sys # stderr.write()
import time # strftime
import os # os.path.isfile() os.path.isdir() os.path.mkdir()
try:
	import atexit
except:
	pass

verbosity = 3
logfile_is_open = 0

def set_verbosity(value):
	global verbosity
	original_verbosity = verbosity
	verbosity = value
	#info(str(verbosity))
	return original_verbosity

def create_new_logfile_with_string(string):
	global logfile_is_open
	logfile_is_open = 0
	global logfile
	try:
		logdirname = "logs"
		try:
			os.mkdir(logdirname)
			info("created dir \"" + logdirname + "\"")
		except:
			pass
		try:
			timestring = time.strftime("%Y-%m-%d.%H%M%S")
			logfilename = logdirname + "/" + timestring + "." + string + ".log"
		except:
			logfilename = logdirname + "/" + string + ".log"
		#info("logfilename = " + logfilename)
#		if os.path.isfile(logfilename):
#			error("ERROR opening logfile %s (file already exists), exiting" % logfilename)
#			sys.exit(1)
		try:
			logfile = open(logfilename, "a")
			#info("logfilename = " + logfilename)
		except:
			try:
				logfilename = string + ".log"
				#info("logfilename = " + logfilename)
				logfile = open(logfilename, "a")
			except:
				pass
		try:
			atexit.register(cleanup)
		except:
			pass
		try:
			info("Writing output from %s to logfile: %s" % (sys.argv[0], logfilename))
		except:
			pass
		logfile_is_open = 1
	except:
		error("Unable to open logfile")

def create_new_logfile_with_string_embedded(dirname, basename, timestring=""):
	global logfile_is_open
	logfile_is_open = 0
	global logfile
	try:
		if ""==timestring:
			filename = dirname + "/" + basename + ".log"
		else:
			filename = dirname + "/" + timestring + "." + basename + ".log"
		logfile = open(filename, "a")
		logfile_is_open = 1
		info("Writing output to logfile: %s" % filename)
	except:
		error("Unable to open logfile")

def print_string_stdout(string, should_flush=1):
	print(string)
	if should_flush:
		try:
			sys.stdout.flush()
		except:
			pass

def print_string_stderr(string, should_flush=1):
	sys.stderr.write(string + "\n")
	if should_flush:
		try:
			sys.stderr.flush()
		except:
			pass

def print_string_logfile(string, should_flush=1):
	if logfile_is_open:
		logfile.write(string + "\n")
		logfile.flush()
		#print("wrote to logfile")
		if should_flush:
			logfile.flush()

def debug3(string, should_flush=1):
	if verbosity>=6:
		string = "  DEBUG3:  " + string
		print_string_stdout(string, should_flush)
		print_string_logfile(string, should_flush)

def debug2(string, should_flush=1):
	if verbosity>=5:
		string = "  DEBUG2:  " + string
		print_string_stdout(string, should_flush)
		print_string_logfile(string, should_flush)

def debug(string, should_flush=1):
	if verbosity>=4:
		string = "   DEBUG:  " + string
		print_string_stdout(string, should_flush)
		print_string_logfile(string, should_flush)

def info(string, should_flush=1):
	if verbosity>=3:
		print_string_stdout(string, should_flush)
		print_string_logfile(string, should_flush)

def warning(string, should_flush=1):
	if verbosity>=2:
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

