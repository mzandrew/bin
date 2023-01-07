#!/usr/bin/env python3

# written 2023-01-04 by mza
# with help from https://realpython.com/pygame-a-primer/#displays-and-surfaces
# last updated 2023-01-06 by mza

SCREEN_WIDTH = 720
SCREEN_HEIGHT = 720
GAP_X_BETWEEN_PLOTS = 14
GAP_Y_BETWEEN_PLOTS = 44
GAP_X_SIDE = 10
GAP_Y_TOP = 24
GAP_Y_BOTTOM = 24
FONT_SIZE_PLOT_CAPTION = 18
FONT_SIZE_FEED_NAME = 16
FONT_SIZE_FEED_NAME_EXTRA_GAP = 6
ICON_SIZE = 32
ICON_BORDER = 2
ICON_SQUARE_LENGTH = ICON_SIZE//2 - 3*ICON_BORDER

ROWS = 2
COLUMNS = 2
plot_name = [ [ "" for j in range(ROWS) ] for i in range(COLUMNS) ]
feed_name = [ [ [] for j in range(ROWS) ] for i in range(COLUMNS) ]
short_feed_name = [ [ [] for j in range(ROWS) ] for i in range(COLUMNS) ]
minimum = [ [ 0 for j in range(ROWS) ] for i in range(COLUMNS) ]
maximum = [ [ 100 for j in range(ROWS) ] for i in range(COLUMNS) ]

plot_name[0][0] = "temperature"
minimum[0][0] = 10.
maximum[0][0] = 80.
feed_name[0][0] = [ "roof-temp", "outdoor-temp", "inside-temp", "heater" ]
short_feed_name[0][0] = [ "roof", "outdoor", "inside", "heater" ]

plot_name[1][0] = "humidity"
minimum[1][0] = 40.
maximum[1][0] = 100.
feed_name[1][0] = [ "roof-hum", "outdoor-hum", "inside-hum", "indoor2-hum" ]
short_feed_name[1][0] = [ "roof", "outdoor", "inside", "indoor2" ]

plot_name[0][1] = "pressure"
minimum[0][1] = 0.997
maximum[0][1] = 1.008
feed_name[0][1] = [ "pressure", "indoor2-pressure" ]
short_feed_name[0][1] = [ "pressure", "indoor2" ]

plot_name[1][1] = "particle count"
minimum[1][1] = 0.
maximum[1][1] = 350.
feed_name[1][1] = [ "indoor-0p3", "indoor-0p5", "indoor-1p0", "indoor-2p5", "indoor-5p0", "particle0p3", "particle0p5", "particle1p0", "particle2p5", "particle5p0", "particle10p0" ]
short_feed_name[1][1] = [ "b3", "b5", "1b0", "2b5", "5b0", "g3", "g5", "1g0", "2g5", "5g0", "10g0" ]

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
import os
os.environ['SDL_AUDIODRIVER'] = 'dsp'
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame # sudo apt install -y python3-pygame
from pygame.locals import K_UP, K_DOWN, K_LEFT, K_RIGHT, K_ESCAPE, KEYDOWN, QUIT, K_q, K_BREAK, K_SPACE
import fetch

FAKE_DATA = False

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
	if values is None:
		values = []
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
		if not FAKE_DATA:
			#feed_data[i][j][k] = fetch.fetch_list_with_datestamps(feed_name[i][j][k], count=plot_width)
			feed_data[i][j][k] = fetch.fetch_simple_list(feed_name[i][j][k], count=plot_width)
			print("length of returned data = " + str(len(feed_data[i][j][k])))
			time.sleep(0.350)
		#feed_data[i][j][k] = [ DEFAULT_VALUE for a in range(plot_width//2) ]
		feed_data[i][j][k] = pad_data_if_insufficient(feed_data[i][j][k], plot_width)
		#print("length of data = " + str(len(feed_data[i][j][k])))

def update_plots():
	#clear_plots()
	for i in range(COLUMNS):
		for j in range(ROWS):
			update_plot(i, j)

def update_plot(i, j):
	for k in range(len(feed_name[i][j])):
		if not FAKE_DATA:
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

def draw_plot_border(i, j):
	print("drawing plot border...")
	pygame.draw.rect(screen, white, pygame.Rect(GAP_X_SIDE+i*(plot_width+GAP_X_BETWEEN_PLOTS)-1, GAP_Y_TOP+j*(plot_height+GAP_Y_BETWEEN_PLOTS)-1, plot_width+2, plot_height+2), 1)

def setup():
	fetch.setup()
	global plot_width
	global plot_height
	global screen
	global plot
	usable_width = SCREEN_WIDTH - 2*GAP_X_SIDE - (COLUMNS-1)*GAP_X_BETWEEN_PLOTS
	#print("usable_width: " + str(usable_width))
	usable_height = SCREEN_HEIGHT - GAP_Y_TOP - GAP_Y_BOTTOM - (ROWS-1)*GAP_Y_BETWEEN_PLOTS
	#print("usable_height: " + str(usable_height))
	plot_width = int(usable_width / COLUMNS)
	plot_height = int(usable_height / ROWS)
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
	pygame.mouse.set_cursor((8,8),(0,0),(0,0,0,0,0,0,0,0),(0,0,0,0,0,0,0,0))
	pygame.display.set_caption("mondrian")
	plot_caption_font = pygame.font.SysFont("monospace", FONT_SIZE_PLOT_CAPTION )
	feed_name_font = pygame.font.SysFont("monospace", FONT_SIZE_FEED_NAME)
#	icon = pygame.Surface((ICON_SIZE, ICON_SIZE))
#	for i in range(COLUMNS):
#		for j in range(ROWS):
#			pass
#			#pygame.draw.rect(icon, (random.randrange(0, 255), random.randrange(0, 255), random.randrange(0, 255)), pygame.Rect(ICON_BORDER+i*(ICON_SQUARE_LENGTH+ICON_BORDER), ICON_BORDER+j*(ICON_SQUARE_LENGTH+ICON_BORDER), ICON_SQUARE_LENGTH, ICON_SQUARE_LENGTH))
#	icon.fill(yellow)
#	pygame.display.set_icon(icon)
	screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
	screen.fill(black)
	plot = [ [ pygame.Surface((plot_width, plot_height)) for j in range(ROWS) ] for i in range(COLUMNS) ]
	#plot_rect = [ [ plot[i][j].get_rect() for j in range(ROWS) ] for i in range(COLUMNS) ]
	#clear_plots()
	for i in range(COLUMNS):
		for j in range(ROWS):
			pygame.event.pump()
			plot_caption = plot_caption_font.render(plot_name[i][j], 1, white)
			screen.blit(plot_caption, plot_caption.get_rect(center=(GAP_X_SIDE+i*(plot_width+GAP_X_BETWEEN_PLOTS)+plot_width//2 , GAP_Y_TOP+j*(plot_height+GAP_Y_BETWEEN_PLOTS)-FONT_SIZE_PLOT_CAPTION//2-4)))
			feed_caption = []
			width = 0
			for k in range(len(short_feed_name[i][j])):
				feed_caption.append(feed_name_font.render(short_feed_name[i][j][k], 1, color[k+2]))
				width += feed_caption[k].get_width() + FONT_SIZE_FEED_NAME_EXTRA_GAP
			print("width: " + str(width))
			for k in range(len(short_feed_name[i][j])):
				screen.blit(feed_caption[k], feed_caption[k].get_rect(center=(GAP_X_SIDE+i*(plot_width+GAP_X_BETWEEN_PLOTS)+plot_width//2-width//2+feed_caption[k].get_width()//2, GAP_Y_TOP+j*(plot_height+GAP_Y_BETWEEN_PLOTS)+plot_height+FONT_SIZE_FEED_NAME//2+4)))
				width -= 2*(feed_caption[k].get_width() + FONT_SIZE_FEED_NAME_EXTRA_GAP)
			print("width: " + str(width))
			fetch_data_for_the_first_time(i, j)
			draw_plot_border(i, j)
			update_plot(i, j)
			blit(i, j)
			flip()
	global should_check_for_new_data
	should_check_for_new_data = pygame.USEREVENT + 1
	pygame.time.set_timer(should_check_for_new_data, 60000)

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
		screen.blit(plot[i][j], (GAP_X_SIDE+i*(plot_width+GAP_X_BETWEEN_PLOTS), GAP_Y_TOP+j*(plot_height+GAP_Y_BETWEEN_PLOTS)))
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

