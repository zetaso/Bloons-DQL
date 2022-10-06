import pygame as pg
import pygame.mouse as mouse
import numpy as np
import random
import sys
import math
from pygame import gfxdraw

sign_fix = -1

def draw():
	background_sprite.draw()
	for i in range(columns):
		for j in range(rows):
			if bloon_sprites[i][j] != None:
				bloon_sprites[i][j].draw()
	monkey_sprite.draw()
	arm_sprite.draw()
	dart_sprite.draw()
	pg.display.update()

class Sprite:
	def __init__(self, x, y, img_src, w, h):
		self.x = x
		self.y = y
		self.w = w
		self.h = h
		self.tx = x - w / 2
		self.ty = y - h / 2
		self.tw = w
		self.th = h
		self.source = pg.image.load("sprites/" + img_src)
		self.image = pg.transform.scale(self.source, (w, h))
		self.angle = 0

	def set_center(self, x, y):
		self.x = x
		self.y = y
		self.tx = x - self.w / 2
		self.ty = y - self.h / 2

	def update(self):
		self.tx = self.x - self.tw / 2
		self.ty = self.y - self.th / 2

	def set_angle(self, new_angle):
		return
		if self.angle == new_angle:
			return
		self.angle = new_angle
		rad_angle = self.angle * np.pi / 180.0
		self.image = pg.transform.scale(self.source, (self.w, self.h))
		self.image = pg.transform.rotate(self.image, sign_fix * self.angle)
		if np.cos(rad_angle) * np.sin(rad_angle) >= 0:
			self.tw = np.absolute(self.w * np.cos(rad_angle) + self.h * np.sin(rad_angle))
			self.th = np.absolute(self.w * np.sin(rad_angle) + self.h * np.cos(rad_angle))
		else:
			self.tw = np.absolute(self.w * np.cos(rad_angle) - self.h * np.sin(rad_angle))
			self.th = np.absolute(self.w * np.sin(rad_angle) - self.h * np.cos(rad_angle))
		self.tx = self.x - self.tw / 2
		self.ty = self.y - self.th / 2

	def draw(self):
		surface.blit(self.image, (self.tx, self.ty))

#	Variables
framerate = 60
delta_time = 0.0008

columns = 20
rows = 10

cell_width = 57
cell_height = 80

width = columns * cell_width
height = rows * cell_height

mouse_angle = 0

	#	Bloons
bloons_data = []
for i in range(columns):
	bloons_data.append([])
	for j in range(rows):
		if i >= columns / 2 and i < columns - 1 and (j == 2 or j == 4 or j == 6):
			bloons_data[i].append(1)
		else:
			bloons_data[i].append(0)

	#	Monkey
monkey_initial_position = [2, 7]	# x and y positions (on the grid)

	#	Dart
flying = False
dart_speed = 2400
dart_velocity = [0, 0]
dart_gravity = 3840

#	Pygame
pg.init()
pg.display.set_icon(pg.image.load("sprites/monkey.png"))
surface = pg.display.set_mode((columns * cell_width, rows * cell_height))
clock = pg.time.Clock()

#	Sprites
background_sprite = Sprite(width / 2, height / 2, "background.png", width, height)
bloon_img = "red_bloon", "green_bloon", "blue_bloon", "yellow_bloon"

bloon_sprites = []
for i in range(columns):
	bloon_sprites.append([])
	for j in range(rows):
		if bloons_data[i][j] == 1:
			bloon_sprites[i].append(Sprite((i + 0.5) * cell_width, (j + 0.5) * cell_height, bloon_img[random.randrange(4)] + ".png", cell_width, cell_height))
			#bloon_sprites[i][j].set_angle(random.randrange(11) - 5)
		else:
			bloon_sprites[i].append(None)

monkey_sprite = Sprite(2.5 * cell_width, 7.5 * cell_height, "monkey.png", 148, 116)
arm_sprite = Sprite(0, 0, "monkey_arm_centered.png", 196, 196)
arm_sprite.set_center(monkey_sprite.x - 25, monkey_sprite.y - 5)
dart_sprite = Sprite(0, 0, "dart.png", 136, 136)

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
		dart_velocity[1] = dart_speed * np.sin(mouse_angle * np.pi / 180.0)
		magnitude = np.sqrt(dart_velocity[0]**2 + dart_velocity[1]**2)
		dart_sprite.x = monkey_sprite.x + dart_velocity[0] / magnitude
		dart_sprite.y = monkey_sprite.y + dart_velocity[1] / magnitude
		dart_sprite.update()

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

	mouse_angle = math.atan2(mouse_y - monkey_sprite.y, mouse_x - monkey_sprite.x) * 180.0 / np.pi

	if flying:
		arm_sprite.set_angle(mouse_angle)
	else:
		arm_sprite.set_angle(mouse_angle + 60)

	if not flying:
		arm_length = 30
		dart_sprite.x = arm_sprite.x + arm_length * np.cos(arm_sprite.angle * np.pi / 180.0)
		dart_sprite.y = arm_sprite.y + arm_length * np.sin(arm_sprite.angle * np.pi / 180.0)
		dart_sprite.update()
		dart_sprite.set_angle(mouse_angle)
	else:
		#dart_velocity[0] -= (dart_velocity[0] * dart_velocity[0]) * 0.0002 * delta_time	#roze con el aire en la componente horizontal de la velocidad
		dart_velocity[1] += dart_gravity * delta_time
		dart_velocity_angle = math.atan2(dart_velocity[1], dart_velocity[0]) * 180 / np.pi
		dart_sprite.x += dart_velocity[0] * delta_time
		dart_sprite.y += dart_velocity[1] * delta_time
		dart_sprite.update()
		dart_sprite.set_angle(dart_velocity_angle)

		tip = [0, 0]
		tip[0] = dart_sprite.x + dart_sprite.w / 2 * np.cos(dart_velocity_angle * np.pi / 180.0)
		tip[1] = dart_sprite.y + dart_sprite.w / 2 * np.sin(dart_velocity_angle * np.pi / 180.0)

		pop = [-1, -1]
		pop[0] = int(tip[0] / cell_width)
		pop[1] = int(tip[1] / cell_height)

		if pop[0] >= 0 and pop[0] < columns and pop[1] >= 0 and pop[1] < rows and bloons_data[pop[0]][pop[1]] == 1:
			bloons_data[pop[0]][pop[1]] = 0
			bloon_sprites[pop[0]][pop[1]] = None

	draw()
	delta_time = clock.tick_busy_loop(framerate) / 1000.0
	pg.display.set_caption("Bloons AI - FPS: " + str(int(clock.get_fps())))

pg.quit()