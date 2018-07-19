#!/usr/bin/python
# python port of DebugInfoWarningError
# started 2015-09-16 by mza
# last updated 2018-07-18 by mza

# usage:
# from DebugInfoWarningError import debug, info, warning, error, debug2, set_verbosity
# set_verbosity(4)
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

def prepare_message(*message):
	first = True
	for msg in message:
		if first:
			string = msg
			first = False
		else:
			string += " " + msg
	return string

def print_message(*message):
	print(prepare_message(*message))

def debug2(*message):
	if (verbosity>=5):
		print_message(*((" DEBUG2:  ",) + message))

def debug(*message):
	if (verbosity>=4):
		print_message(*(("  DEBUG:  ",) + message))

def info(*message):
	if (verbosity>=3):
		#print_message(*(("INFO:  ",) + message))
		print_message(*message)

def warning(*message):
	if (verbosity>=2):
		print_message(*(("WARNING:  ",) + message))

#def error(*message, level=0):
def error(*message):
	# from http://stackoverflow.com/questions/5574702/how-to-print-to-stderr-in-python
	if (verbosity>=1):
		print(prepare_message(*(("  ERROR:  ",) + message)), file=sys.stderr)
#		if (level>0):
#			exit(level)

