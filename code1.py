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
	surface.blit(dart_sprite, dart_sprite_position)
	pg.display.update()

#	Variables
framerate = 120

rows = 10
columns = 20

cell_width = 57
cell_height = 80

mouse_angle = 0

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

	#	Dart
flying = False
dart_speed = 1920
dart_velocity = [0, 0]
dart_gravity = 3840

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
monkey_sprite_position = [monkey_initial_position[0] * cell_width - 98, monkey_initial_position[1] * cell_height - 98]

arm_angle = 0
monkey_arm = pg.image.load("sprites/monkey_arm_centered.png")
arm_sprite = pg.transform.scale(monkey_arm, (196, 196))
arm_sprite = pg.transform.rotate(arm_sprite, arm_angle)
arm_sprite_position = [0, 0]

dart = pg.image.load("sprites/dart.png")
dart_sprite = pg.transform.scale(dart, (136, 136))
dart_sprite = pg.transform.rotate(dart_sprite, mouse_angle)
dart_sprite_position = [0, 0]
dart_real_position = [0, 0]

#	Juego
run = True
while run:
	for event in pg.event.get():
		if event.type == pg.QUIT:
			run = False

	#keys = pg.key.get_pressed()
	[mouse_x, mouse_y] = mouse.get_pos()

	#left_onpress = not left_click
	left_click = mouse.get_pressed(3)[0]
	if left_click and not flying:
		flying = True
		dart_velocity[0] = dart_speed * np.cos(mouse_angle * np.pi / 180.0)
		dart_velocity[1] = - dart_speed * np.sin(mouse_angle * np.pi / 180.0)
		magnitude = np.sqrt(dart_velocity[0]**2 + dart_velocity[1]**2)
		dart_real_position[0] = monkey_sprite_position[0] + 98 + cell_width / 2 + dart_velocity[0] / magnitude
		dart_real_position[1] = monkey_sprite_position[1] + 98 + cell_height / 2 + dart_velocity[1] / magnitude
	#left_onpress = left_onpress and left_click
	right_click = mouse.get_pressed(3)[2]
	if right_click:
		flying = False

	#if (left_click or right_click) and search_state[0] == 2:
	#	search_state[0] = 0
	#	state = "Idle"
	#	state_color[0] = white
	#	state_text[0] = font.render(state, True, state_color[0], None)

	#check_button_hovers(mouse_x, mouse_y, left_click, left_onpress)

	draw()
	delta_time = clock.tick_busy_loop(60) / 1000.0
	delta_time = 0.0008
	pg.display.set_caption("Bloons AI - FPS: " + str(int(clock.get_fps())))

	mouse_angle = - math.atan2(mouse_y - (monkey_sprite_position[1] + 98 + 33), mouse_x - (monkey_sprite_position[0] + 98 + 5)) * 180.0 / np.pi

	arm_angle = mouse_angle + 135
	arm_sprite = pg.transform.scale(monkey_arm, (196, 196))
	arm_sprite = pg.transform.rotate(arm_sprite, arm_angle)

	dx = 98 * (np.cos(arm_angle * np.pi / 180.0) + np.sin(arm_angle * np.pi / 180.0))
	dy = 98 * (np.cos(arm_angle * np.pi / 180.0) - np.sin(arm_angle * np.pi / 180.0))
	offset = max(abs(dx), abs(dy)) - 98

	arm_sprite_position[0] = monkey_sprite_position[0] - offset + 5
	arm_sprite_position[1] = monkey_sprite_position[1] - offset + 33

	if not flying:
		arm_length = 30
		dart_sprite = pg.transform.scale(dart, (136, 136))
		dart_sprite = pg.transform.rotate(dart_sprite, mouse_angle)

		dx = 68 * (np.cos(mouse_angle * np.pi / 180.0) + np.sin(mouse_angle * np.pi / 180.0))
		dy = 68 * (np.cos(mouse_angle * np.pi / 180.0) - np.sin(mouse_angle * np.pi / 180.0))
		offset = max(abs(dx), abs(dy)) - 68

		dart_sprite_position[0] = monkey_sprite_position[0] + 98 + 5 + arm_length * np.cos(arm_angle * np.pi / 180.0) - 68 - offset
		dart_sprite_position[1] = monkey_sprite_position[1] + 98 + 33 - arm_length * np.sin(arm_angle * np.pi / 180.0) - 68 - offset
	else:
		dart_velocity[1] += dart_gravity * delta_time
		dart_angle = - math.atan2(dart_velocity[1], dart_velocity[0]) * 180 / np.pi
		dart_real_position[0] += dart_velocity[0] * delta_time
		dart_real_position[1] += dart_velocity[1] * delta_time

		dart_sprite_position[0] = dart_real_position[0] - 68
		dart_sprite_position[1] = dart_real_position[1] - 68
		dart_sprite = pg.transform.scale(dart, (136, 136))
		dart_sprite = pg.transform.rotate(dart_sprite, dart_angle)

		dx = 68 * (np.cos(mouse_angle * np.pi / 180.0) + np.sin(mouse_angle * np.pi / 180.0))
		dy = 68 * (np.cos(mouse_angle * np.pi / 180.0) - np.sin(mouse_angle * np.pi / 180.0))
		offset = max(abs(dx), abs(dy)) - 68

		dart_sprite_position[0] += - offset
		dart_sprite_position[1] += - offset

pg.quit()