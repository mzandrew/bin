#!/usr/bin/env python3

# written 2022-04-30 by mza
# last updated 2022-04-30 by mza

import airlift
import generic

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
	for i in range(len(myarray)):
		datestamp = myarray[i][0]
		datestamp = generic.convert_date_to_local_time(datestamp)
		value     = myarray[i][1]
		print(str(datestamp) + "," + str(value))

airlift.setup_io()
#feed = "outdoor-hum"
#fetch_simple_list()
feed = "steps"
fetch_list_with_datestamps()

