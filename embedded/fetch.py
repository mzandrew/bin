#!/usr/bin/env python3

# written 2022-04-30 by mza
# last updated 2022-06-16 by mza

import airlift
import generic

header = "id,value,feed_id,created_at,lat,lon,ele"

def fetch_simple_list():
	#myarray = airlift.get_all_data(feed, 215)
	myarray = airlift.get_all_data(feed)
	for i in range(len(myarray)):
		value     = myarray[i]
		print(str(value))

def fetch_list_with_datestamps():
	#myarray = airlift.get_all_data_with_datestamps(feed, 215)
	myarray = airlift.get_all_data_with_datestamps(feed)
	#print(str(len(myarray)))
	print(header)
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
		print(str(id) + "," + str(value) + "," + str(feed_id) + "," + str(created_at) + "," + str(lat) + "," + str(lon) + "," + str(ele))

airlift.setup_io()
#feed = "outdoor-hum"
#fetch_simple_list()
feed = "steps"
#feed = "wifi"
fetch_list_with_datestamps()

