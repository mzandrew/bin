#!/usr/bin/env python3

# written 2022-04-30 by mza
# last updated 2024-03-23 by mza

# if we try to specify the number of items to return, we now get this:
# EXCEPTION:  Client.data() got an unexpected keyword argument 'max_results'
# docs still say this should work:
# https://adafruit-io-python-client.readthedocs.io/en/latest/data.html#data-retrieval
# which also says receive_next and receive_previous should work

# https://forums.adafruit.com/viewtopic.php?p=923009&hilit=max_results#p923009
# so we must do:
# pip3 install adafruit-io --upgrade --force-reinstall

#COUNT = 1000
COUNT = 10000
#COUNT = None # this means "all"

import sys
import time
import airlift
import generic
import datetime

header = "id,value,feed_id,created_at,lat,lon,ele"

def add_most_recent_data_to_end_of_array(values, feed):
	return airlift.add_most_recent_data_to_end_of_array(values, feed)

def fetch_simple_list_hmmm(feed_name, count=COUNT):
	myarray = airlift.get_all_data(feed_name, count)
#	for i in range(len(myarray)):
#		value = myarray[i]
#		#print(str(value))
	return myarray

def fetch_simple_list(feed_name, count=COUNT):
	myarray = airlift.get_some_data(feed_name, count)
	for i in range(len(myarray)):
		value = myarray[i]
		print(str(value))
	return myarray

def fetch_list_with_datestamps(feed_name, count=COUNT):
	myarray = airlift.get_all_data_with_datestamps(feed_name, count)
	#print(str(len(myarray)))
	mynewarray = []
	mynewarray.append(header)
	for i in range(len(myarray)):
		id,value,feed_id,created_at,lat,lon,ele = myarray[i]
		#created_at = generic.convert_date_to_local_time(created_at)
		created_at = generic.convert_date_to_UTC_time(created_at)
		#print(str(created_at) + "," + str(value))
		if None==lat:
			lat=""
		if None==lon:
			lon=""
		if None==ele:
			ele=""
		mynewarray.append(str(id) + "," + str(value) + "," + str(feed_id) + "," + str(created_at) + "," + str(lat) + "," + str(lon) + "," + str(ele))
	return mynewarray

def fetch_list_with_datestamps_and_write_to_file(arg):
	filename = timestamp + "." + arg + ".csv"
	print("fetching " + arg + " to " + filename + " ...")
	with open(filename, "w") as myfile:
		for line in fetch_list_with_datestamps(arg):
			myfile.write(line)
			myfile.write("\n")
	#generic.show_filesize(filename)
	#generic.show_linecount(filename)
	generic.show_wc(filename)
	time.sleep(1)

def grab_a_bunch():
	myfeeds = [ "garage-0p3", "garage-0p5", "garage-1p0", "garage-2p5", "garage-5p0", "garage-10p0" ]
	for feed in myfeeds:
		fetch_list_with_datestamps_and_write_to_file(feed)
	myfeeds = [ "3d-printer-0p3", "3d-printer-0p5", "3d-printer-1p0", "3d-printer-2p5", "3d-printer-5p0" ]
	for feed in myfeeds:
		fetch_list_with_datestamps_and_write_to_file(feed)

def setup():
	airlift.setup_io()

if "__main__"==__name__:
	setup()
	timestamp = datetime.datetime.utcnow().replace(microsecond=0,tzinfo=datetime.timezone.utc).strftime("%Y-%m-%d.%H%M%S")
	if 1<len(sys.argv):
		for arg in sys.argv[1:]:
			#fetch_simple_list(arg)
			fetch_list_with_datestamps_and_write_to_file(arg)
	else:
		#grab_a_bunch()
		print("fetch what?")

