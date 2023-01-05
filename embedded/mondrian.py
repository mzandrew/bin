#!/usr/bin/env python3

# written 2023-01-04 by mza
# with help from https://realpython.com/pygame-a-primer/#displays-and-surfaces
# last updated 2023-01-04 by mza

SCREEN_WIDTH = 720
SCREEN_HEIGHT = 720
GAP_X_BETWEEN_PLOTS = 10
GAP_Y_BETWEEN_PLOTS = 10
GAP_X_SIDE = 10
GAP_Y_TOP_BOTTOM = 10

ROWS = 2
COLUMNS = 2
plot_name = [ [ "" for j in range(ROWS) ] for i in range(COLUMNS) ]
feed_name = [ [ [] for j in range(ROWS) ] for i in range(COLUMNS) ]
plot_name[0][0] = "temp"
feed_name[0][0] = [ "heater", "inside-temp" ]
plot_name[0][1] = "hum"
feed_name[0][1] = [ "indoor2-hum", "inside-hum" ]
plot_name[1][0] = "pres"
feed_name[1][0] = [ "indoor2-pressure", "pressure" ]
plot_name[1][1] = "particle"
feed_name[1][1] = [ "indoor-1p0", "particle1p0" ]

import sys
import time
import random
#import adafruit_blinka
import pygame
from pygame.locals import K_UP, K_DOWN, K_LEFT, K_RIGHT, K_ESCAPE, KEYDOWN, QUIT, K_q, K_BREAK, K_SPACE
import fetch

black = (0, 0, 0)

def clear_plot(i, j):
	plot[i][j].fill(black)

def clear_plots():
	for i in range(COLUMNS):
		for j in range(ROWS):
			plot[i][j].fill(black)

#def draw_borders():
#	for i in range(COLUMNS):
#		for j in range(ROWS):
#			for k in range(padding_size//2, tile_width-padding_size//2):
#				axes_bitmap[k,padding_size//2] = 1
#				axes_bitmap[k,tile_height-padding_size//2] = 1
#			for k in range(padding_size//2, tile_height-padding_size//2):
#				axes_bitmap[padding_size//2,k] = 1
#				axes_bitmap[tile_width-padding_size//2,k] = 1

DEFAULT_VALUE = -40
def pad_data_if_insufficient(values, count_desired):
	count_gotten = len(values)
	if count_desired is not None:
		if count_desired<count_gotten:
			values = values[:count_desired]
		elif count_gotten<count_desired:
			for i in range(count_gotten, count_desired):
				values.append(DEFAULT_VALUE)
	return values

def update_plots_for_the_first_time():
	for i in range(COLUMNS):
		for j in range(ROWS):
			print(plot_name[i][j])
			for k in range(len(feed_name[i][j])):
				print("fetching data for feed \"" + feed_name[i][j][k] + "\"...")
				if 0==i and 0==j and 0==k:
					pass
					#feed_data[i][j][k] = fetch.fetch_simple_list(feed_name[i][j][k], count=plot_width)
					#feed_data[i][j][k] = fetch.fetch_list_with_datestamps(feed_name[i][j][k], count=plot_width)
				#print("length of returned data = " + str(len(feed_data[i][j][k])))
				feed_data[i][j][k] = [ DEFAULT_VALUE for a in range(plot_width//2) ]
				feed_data[i][j][k] = pad_data_if_insufficient(feed_data[i][j][k], plot_width)
				print("length of data = " + str(len(feed_data[i][j][k])))
				time.sleep(0.350)

def update_plots():
	clear_plots()
	for i in range(COLUMNS):
		for j in range(ROWS):
			for k in range(len(feed_name[i][j])):
				print("fetching another datapoint for feed \"" + feed_name[i][j][k] + "\"...")
				feed_data[i][j][k] = fetch.add_most_recent_data_to_end_of_array(feed_data[i][j][k], feed_name[i][j][k])
				print("length of data = " + str(len(feed_data[i][j][k])))
	global plots_were_updated
	for i in range(COLUMNS):
		for j in range(ROWS):
			# fill with colors for now:
			plot[i][j].fill((random.randrange(0, 255), random.randrange(0, 255), random.randrange(0, 255)))
#			for x in range(plot_width):
#				for k in range(len(feed_name[i][j])):
			plots_were_updated[i][j] = True

def setup():
	fetch.setup()
	global plot_width
	global plot_height
	global screen
	global plot
	usable_width = SCREEN_WIDTH - 2*GAP_X_SIDE - (COLUMNS-1)*GAP_X_BETWEEN_PLOTS
	#print("usable_width: " + str(usable_width))
	usable_height = SCREEN_HEIGHT - 2*GAP_Y_TOP_BOTTOM - (ROWS-1)*GAP_Y_BETWEEN_PLOTS
	#print("usable_height: " + str(usable_height))
	plot_width = int(usable_width / COLUMNS)
	plot_height = int(usable_width / ROWS)
	#print("plot_width: " + str(plot_width))
	#print("plot_height: " + str(plot_height))
	global feed_data
	feed_data = [ [ [] for j in range(ROWS) ] for i in range(COLUMNS) ]
	for i in range(COLUMNS):
		for j in range(ROWS):
			for k in range(len(feed_name[i][j])):
				feed_data[i][j].append([ DEFAULT_VALUE for x in range(plot_width) ])
	pygame.init()
	#size = (pygame.display.Info().current_w, pygame.display.Info().current_h)
	size = (SCREEN_WIDTH, SCREEN_HEIGHT)
	screen = pygame.display.set_mode(size)
	screen.fill(black)
	plot = [ [ pygame.Surface((plot_width, plot_height)) for j in range(ROWS) ] for i in range(COLUMNS) ]
	#plot_rect = [ [ plot[i][j].get_rect() for j in range(ROWS) ] for i in range(COLUMNS) ]
	clear_plots()
	update_plots_for_the_first_time()
	global should_check_for_new_data
	should_check_for_new_data = pygame.USEREVENT + 1
	pygame.time.set_timer(should_check_for_new_data, 60000)

def update_display():
	global running
	global should_update_plots
	global plots_were_updated
	#pressed_keys = pygame.key.get_pressed()
	for event in pygame.event.get():
		if event.type == KEYDOWN:
			if K_ESCAPE==event.key or K_q==event.key:
				running = False
			elif K_SPACE==event.key:
				should_update_plots = True
		elif event.type == QUIT:
			running = False
		elif event.type == should_check_for_new_data:
			should_update_plots = True
	if should_update_plots:
		print("updating...")
		should_update_plots = False
		update_plots()
	something_was_updated = False
	for i in range(COLUMNS):
		for j in range(ROWS):
			if plots_were_updated[i][j]:
				screen.blit(plot[i][j], (GAP_X_SIDE+i*(plot_width+GAP_X_BETWEEN_PLOTS), GAP_Y_TOP_BOTTOM+j*(plot_height+GAP_Y_BETWEEN_PLOTS)))
				plots_were_updated[i][j] = False
				something_was_updated = True
		if something_was_updated:
			pygame.display.flip()

running = True
should_update_plots = False
plots_were_updated = [ [ False for j in range(ROWS) ] for i in range(COLUMNS) ]
setup()
while running:
	update_display()
	time.sleep(1)
pygame.quit()

