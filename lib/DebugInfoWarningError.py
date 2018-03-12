#!/usr/bin/python
# python port of DebugInfoWarningError
# started 2015-09-16 by mza

# usage:
# from DebugInfoWarningError import info, debug, debug2, warning, error
# verbosity = 4
# debug("some pedantic stuff here")
# info("this is an informational message")
# warning("you forgot something")
# error("you forgot something important")
# error("you forgot something very important and we will quit", 17)

from __future__ import print_function
import sys

verbosity = 3

def set_verbosity(value):
	global verbosity
	verbosity = value
	#info(str(verbosity))

def debug2(message):
	if (verbosity>=5):
		print("DEBUG:  " + message)

def debug(message):
	if (verbosity>=4):
		print("DEBUG:  " + message)

def info(message):
	if (verbosity>=3):
		print(message)

def warning(message):
	if (verbosity>=2):
		print("WARNING:  " + message, file=sys.stderr)

def error(message, level = 0):
	# from http://stackoverflow.com/questions/5574702/how-to-print-to-stderr-in-python
	if (verbosity>=1):
		print("ERROR:  " + message, file=sys.stderr)
		if (level>0):
			exit(level)

