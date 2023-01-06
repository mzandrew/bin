#!/usr/bin/env python3

# written 2023-01-04 by mza
# with help from https://realpython.com/pygame-a-primer/#displays-and-surfaces
# last updated 2023-01-06 by mza

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
minimum = [ [ 0 for j in range(ROWS) ] for i in range(COLUMNS) ]
maximum = [ [ 100 for j in range(ROWS) ] for i in range(COLUMNS) ]

plot_name[0][0] = "temp"
minimum[0][0] = 10.
maximum[0][0] = 80.
feed_name[0][0] = [ "roof-temp", "outdoor-temp", "inside-temp", "heater" ]

plot_name[1][0] = "hum"
minimum[1][0] = 40.
maximum[1][0] = 100.
feed_name[1][0] = [ "roof-hum", "outdoor-hum", "inside-hum", "indoor2-hum" ]

plot_name[0][1] = "pres"
minimum[0][1] = 0.997
maximum[0][1] = 1.008
feed_name[0][1] = [ "pressure", "indoor2-pressure" ]

plot_name[1][1] = "particle"
minimum[1][1] = 0.
maximum[1][1] = 350.
feed_name[1][1] = [ "indoor-0p3", "indoor-0p5", "indoor-1p0", "indoor-2p5", "indoor-5p0", "particle0p3", "particle0p5", "particle1p0", "particle2p5", "particle5p0", "particle10p0" ]

black = (0, 0, 0)
white = (255, 255, 255)
red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)
yellow = (255, 255, 0)
teal = (0, 255, 255)
purple = (255, 0, 255)
pink = (255, 127, 127)
orange = (255, 127, 0)
dark_green = (0, 127, 0)
light_blue = (127, 127, 255)
maroon = (255, 0, 127)

color = [ black, white, red, green, blue, yellow, teal, purple, pink, orange, dark_green, light_blue, maroon ]

import sys
import time
import random
#import adafruit_blinka
import pygame
from pygame.locals import K_UP, K_DOWN, K_LEFT, K_RIGHT, K_ESCAPE, KEYDOWN, QUIT, K_q, K_BREAK, K_SPACE
import fetch

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

#DEFAULT_VALUE = -40
DEFAULT_VALUE = 35.
def pad_data_if_insufficient(values, count_desired):
	count_gotten = len(values)
	if count_desired is not None:
		if count_desired<count_gotten:
			values = values[:count_desired]
		elif count_gotten<count_desired:
			for i in range(count_gotten, count_desired):
				values.append(DEFAULT_VALUE)
	return values

def format_for_plot(values, minimum, maximum):
	new_values = []
	#print(str(values))
	for i in range(len(values)):
		new_values.append((values[i]-minimum)/(maximum - minimum))
	return new_values

def fetch_data_for_the_first_time(i, j):
	print(plot_name[i][j])
	for k in range(len(feed_name[i][j])):
		print("fetching data for feed \"" + feed_name[i][j][k] + "\"...")
		#if 0==i and 0==j and 0==k:
		#	pass
			#feed_data[i][j][k] = fetch.fetch_list_with_datestamps(feed_name[i][j][k], count=plot_width)
		feed_data[i][j][k] = fetch.fetch_simple_list(feed_name[i][j][k], count=plot_width)
		print("length of returned data = " + str(len(feed_data[i][j][k])))
		#feed_data[i][j][k] = [ DEFAULT_VALUE for a in range(plot_width//2) ]
		feed_data[i][j][k] = pad_data_if_insufficient(feed_data[i][j][k], plot_width)
		print("length of data = " + str(len(feed_data[i][j][k])))
		time.sleep(0.350)

def update_plots():
	#clear_plots()
	for i in range(COLUMNS):
		for j in range(ROWS):
			update_plot(i, j)

def update_plot(i, j):
	for k in range(len(feed_name[i][j])):
		#print("fetching another datapoint for feed \"" + feed_name[i][j][k] + "\"...")
		feed_data[i][j][k] = fetch.add_most_recent_data_to_end_of_array(feed_data[i][j][k], feed_name[i][j][k])
		#print("length of data = " + str(len(feed_data[i][j][k])))
	global plots_were_updated
	print("normalizing data...")
	for k in range(len(feed_name[i][j])):
		normalized_feed_data[i][j][k] = format_for_plot(feed_data[i][j][k], minimum[i][j], maximum[i][j])
	print("plotting data...")
	# fill with colors for now:
	#plot[i][j].fill((random.randrange(0, 255), random.randrange(0, 255), random.randrange(0, 255)))
	print("[" + str(i) + "][" + str(j) + "]")
	for x in range(plot_width):
		for y in range(plot_height):
			plot[i][j].set_at((x, y), black)
			for k in range(len(feed_name[i][j])):
				yn = int(plot_height - plot_height * normalized_feed_data[i][j][k][x])
				doit = False
				if y==yn:
					doit = True
				elif 0==y and yn<0:
					doit = True
				elif plot_height-1==y and plot_height<yn:
					doit = True
				if doit:
					plot[i][j].set_at((x, y), color[k+2]) # first two indices are black and white
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
	global normalized_feed_data
	feed_data = [ [ [] for j in range(ROWS) ] for i in range(COLUMNS) ]
	normalized_feed_data = [ [ [] for j in range(ROWS) ] for i in range(COLUMNS) ]
	for i in range(COLUMNS):
		for j in range(ROWS):
			for k in range(len(feed_name[i][j])):
				feed_data[i][j].append([ DEFAULT_VALUE for x in range(plot_width) ])
				normalized_feed_data[i][j].append([ 0.5 for x in range(plot_width) ])
	pygame.init()
	#size = (pygame.display.Info().current_w, pygame.display.Info().current_h)
	size = (SCREEN_WIDTH, SCREEN_HEIGHT)
	screen = pygame.display.set_mode(size)
	screen.fill(black)
	plot = [ [ pygame.Surface((plot_width, plot_height)) for j in range(ROWS) ] for i in range(COLUMNS) ]
	#plot_rect = [ [ plot[i][j].get_rect() for j in range(ROWS) ] for i in range(COLUMNS) ]
	#clear_plots()
	for i in range(COLUMNS):
		for j in range(ROWS):
			fetch_data_for_the_first_time(i, j)
			update_plot(i, j)
			blit(i, j)
			flip()
	global should_check_for_new_data
	should_check_for_new_data = pygame.USEREVENT + 1
	pygame.time.set_timer(should_check_for_new_data, 15000)

ij = 0
def loop():
	global running
	global should_update_plots
	global ij
	global something_was_updated
	something_was_updated = False
	#pressed_keys = pygame.key.get_pressed()
	for event in pygame.event.get():
		if event.type == KEYDOWN:
			if K_ESCAPE==event.key or K_q==event.key:
				running = False
			elif K_SPACE==event.key:
				should_update_plots = [ [ True for j in range(ROWS) ] for i in range(COLUMNS) ]
		elif event.type == QUIT:
			running = False
		elif event.type == should_check_for_new_data:
			if 0==ij:
				should_update_plots[0][0] = True
			elif 1==ij:
				should_update_plots[0][1] = True
			elif 2==ij:
				should_update_plots[1][0] = True
			elif 3==ij:
				should_update_plots[1][1] = True
			ij += 1
			if 3<ij:
				ij = 0
	for i in range(COLUMNS):
		for j in range(ROWS):
			if should_update_plots[i][j]:
				#print("updating...")
				should_update_plots[i][j] = False
				update_plot(i, j)
	for i in range(COLUMNS):
		for j in range(ROWS):
			blit(i, j)
	flip()

def blit(i, j):
	global something_was_updated
	if plots_were_updated[i][j]:
		print("blitting...")
		screen.blit(plot[i][j], (GAP_X_SIDE+i*(plot_width+GAP_X_BETWEEN_PLOTS), GAP_Y_TOP_BOTTOM+j*(plot_height+GAP_Y_BETWEEN_PLOTS)))
		plots_were_updated[i][j] = False
		something_was_updated = True

def flip():
	global something_was_updated
	if something_was_updated:
		print("flipping...")
		pygame.display.flip()
		something_was_updated = False

running = True
should_update_plots = [ [ False for j in range(ROWS) ] for i in range(COLUMNS) ]
plots_were_updated = [ [ False for j in range(ROWS) ] for i in range(COLUMNS) ]
setup()
while running:
	loop()
	time.sleep(1)
pygame.quit()

