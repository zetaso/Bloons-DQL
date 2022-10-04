import pygame as pg
import pygame.mouse as mouse
import numpy as np
import random
import sys
import math
from pygame import gfxdraw

def draw():
	surface.blit(background_sprite, (0, 0))
	for i in range(rows):
		for j in range(columns):
			if bloons_data[i][j] > 0:
				surface.blit(bloon_sprites[bloons_data[i][j] - 1], (j * cell_width, i * cell_height))
	surface.blit(monkey_sprite, monkey_sprite_position)
	surface.blit(arm_sprite, arm_sprite_position)
	pg.display.update()

#	Variables
framerate = 120

rows = 10
columns = 20

cell_width = 57
cell_height = 80

	#	Bloons
bloons_data = []
for i in range(rows):
	bloons_data.append([])
	for j in range(columns):
		if i > 0 and i <= 6 and j > 7 and j <= 17:
			bloons_data[i].append(1 + random.randrange(4))
		else:
			bloons_data[i].append(0)

	#	Monkey
monkey_initial_position = [2, 7]	# x and y positions (on the grid)

#	Pygame
pg.init()
surface = pg.display.set_mode((columns * cell_width, rows * cell_height))
clock = pg.time.Clock()

#	Sprites
background_sprite = pg.image.load("sprites/background.png")

bloon_sprites = []
bloon_sprites.append(pg.image.load("sprites/red_bloon.png"))
bloon_sprites.append(pg.image.load("sprites/green_bloon.png"))
bloon_sprites.append(pg.image.load("sprites/blue_bloon.png"))
bloon_sprites.append(pg.image.load("sprites/yellow_bloon.png"))

for i in range(4):
	bloon_sprites[i] = pg.transform.scale(bloon_sprites[i], (cell_width, cell_height))
	#bloon_sprites[i] = pg.transform.rotate(bloon_sprites[i], random.randrange(11) - 5)

monkey_sprite = pg.image.load("sprites/monkey_centered.png")
monkey_sprite = pg.transform.scale(monkey_sprite, (196, 196))
monkey_sprite_position = monkey_initial_position[0] * cell_width - 98, monkey_initial_position[1] * cell_height - 98

angle = 0
monkey_arm = pg.image.load("sprites/monkey_arm_centered.png")
arm_sprite = pg.transform.scale(monkey_arm, (196, 196))
arm_sprite = pg.transform.rotate(arm_sprite, angle)
arm_sprite_position = []
arm_sprite_position.append(monkey_sprite_position[0] - 196 * ((np.cos(angle * np.pi / 180.0) + np.sin(angle * np.pi / 180.0)) * 0.5))
arm_sprite_position.append(monkey_sprite_position[1] - 196 * ((np.cos(angle * np.pi / 180.0) - np.sin(angle * np.pi / 180.0)) * 0.5))

#	Juego
run = True
while run:
	for event in pg.event.get():
		if event.type == pg.QUIT:
			run = False

	#keys = pg.key.get_pressed()
	[mouse_x, mouse_y] = mouse.get_pos()

	#left_onpress = not left_click
	#left_click = mouse.get_pressed(3)[0]
	#left_onpress = left_onpress and left_click
	#right_click = mouse.get_pressed(3)[2]

	#if (left_click or right_click) and search_state[0] == 2:
	#	search_state[0] = 0
	#	state = "Idle"
	#	state_color[0] = white
	#	state_text[0] = font.render(state, True, state_color[0], None)

	#check_button_hovers(mouse_x, mouse_y, left_click, left_onpress)

	draw()
	delta_time = clock.tick_busy_loop(framerate) / 1000.0
	pg.display.set_caption("Bloons AI - FPS: " + str(int(clock.get_fps())))

	angle += 45 * delta_time
	arm_sprite = pg.transform.scale(monkey_arm, (196, 196))
	arm_sprite = pg.transform.rotate(arm_sprite, angle)

	dx = 98 * (np.cos(angle * np.pi / 180.0) + np.sin(angle * np.pi / 180.0))
	dy = 98 * (np.cos(angle * np.pi / 180.0) - np.sin(angle * np.pi / 180.0))
	offset = max(abs(dx), abs(dy)) - 98

	arm_sprite_position[0] = monkey_sprite_position[0] - offset + 5
	arm_sprite_position[1] = monkey_sprite_position[1] - offset + 33

pg.quit()