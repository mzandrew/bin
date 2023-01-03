#!/usr/bin/env python3

# written 2022-04-30 by mza
# last updated 2023-01-02 by mza

import sys
import time
import airlift
import generic
import datetime

header = "id,value,feed_id,created_at,lat,lon,ele"

def fetch_simple_list(feed_name):
	#myarray = airlift.get_all_data(feed_name, 215)
	myarray = airlift.get_all_data(feed_name)
	for i in range(len(myarray)):
		value     = myarray[i]
		print(str(value))

def fetch_list_with_datestamps(feed_name):
	#myarray = airlift.get_all_data_with_datestamps(feed_name, 215)
	myarray = airlift.get_all_data_with_datestamps(feed_name)
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
	print("fetching " + arg + " to " + filename + "...")
	with open(filename, "w") as myfile:
		for line in fetch_list_with_datestamps(arg):
			myfile.write(line)
			myfile.write("\n")
	time.sleep(1)

def grab_a_bunch():
	myfeeds = [ "particle0p3", "particle0p5", "particle1p0", "particle2p5", "particle5p0", "particle10p0" ]
	for feed in myfeeds:
		fetch_list_with_datestamps_and_write_to_file(feed)
	myfeeds = [ "indoor-0p3", "indoor-0p5", "indoor-1p0", "indoor-2p5", "indoor-5p0" ]
	for feed in myfeeds:
		fetch_list_with_datestamps_and_write_to_file(feed)

if "__main__"==__name__:
	airlift.setup_io()
	timestamp = datetime.datetime.utcnow().replace(microsecond=0,tzinfo=datetime.timezone.utc).strftime("%Y-%m-%d.%H%M%S")
	if 1<len(sys.argv):
		for arg in sys.argv[1:]:
			fetch_list_with_datestamps_and_write_to_file(arg)
	else:
		#grab_a_bunch()
		print("fetch what?")
