import pygame as pg
import pygame.mouse as mouse
import random
import sys
import math

sys.setrecursionlimit(10000)

white = 255, 255, 255
black = 0, 0, 0
red = 255, 0, 0
cyan = 0, 255, 255
purple = 196, 0, 255
green = 0, 255, 0
orange = 255, 102, 0
bg_primary = 130, 120, 119
bg_secondary = 116, 107, 106

player_colors = [red, cyan, purple, orange, white]

pixel = 32

run = True
deltaTime = 0.0
timeMultiplier = [1.0]
defaultCooldown = 0.2
cooldown = defaultCooldown
normalized_cooldown = 1

players = []
init_positions = []
goal_positions = []
moves = []
expanded_nodes = []
combinations = []
viewed_nodes = {}

mapa = []

algorithm = [""]
search = [False]

diagonal = False

dragging = False
player_dragged = -1
goal_dragged = -1

plus_pressed = False
plus_onpress = False
minus_pressed = False
minus_onpress = False

left_click = False
middle_click = False
right_click = False

framerate = 120
sim_framerate = 120
pressing = False

rows = 30
columns = 45

size = width, height = columns * pixel, rows * pixel

pg.init()

surface = pg.display.set_mode(size)
clock = pg.time.Clock()

font = pg.font.Font('pixel.ttf', int(pixel / 2))

add_agent_text = font.render('Add agent', True, white, None)
add_agent_text_rect = add_agent_text.get_rect()
add_agent_text_rect.center = (3 * pixel, pixel)
add_agent_rect = pg.Rect(pixel, pixel / 2, 4 * pixel, pixel)
add_settings = [False, False]

rem_agent_text = font.render('Remove agent', True, white, None)
rem_agent_text_rect = rem_agent_text.get_rect()
rem_agent_text_rect.center = (8.5 * pixel, pixel)
rem_agent_rect = pg.Rect(6 * pixel, pixel / 2, 5 * pixel, pixel)
rem_settings = [False, False]

speed_text = [font.render("{:.1f}%".format(timeMultiplier[0] * 100), True, white, None)]
speed_text_rect = speed_text[0].get_rect()
speed_text_rect.center = (15.5 * pixel, pixel)

increase_text = font.render('+', True, white, None)
increase_text_rect = increase_text.get_rect()
increase_text_rect.center = (18.5 * pixel, pixel)
increase_rect = pg.Rect(18 * pixel, pixel / 2, pixel, pixel)
increase_settings = [False, False]

decrease_text = font.render('-', True, white, None)
decrease_text_rect = decrease_text.get_rect()
decrease_text_rect.center = (13.5 * pixel, pixel)
decrease_rect = pg.Rect(13 * pixel, pixel / 2, pixel, pixel)
decrease_settings = [False, False]

clear_text = font.render('Clear walls', True, white, None)
clear_text_rect = clear_text.get_rect()
clear_text_rect.center = (40.5 * pixel, pixel)
clear_rect = pg.Rect(38 * pixel, pixel / 2, 5 * pixel, pixel)
clear_settings = [False, False]

search_state = [0]
state = "Idle"
state_color = [white]
state_text = [font.render(state, True, state_color[0], None)]
state_text_rect = state_text[0].get_rect()
state_text_rect.center = (25.5 * pixel, pixel)

greedy_text = font.render('Greedy', True, white, None)
greedy_text_rect = greedy_text.get_rect()
greedy_text_rect.center = (3 * pixel, 3 * pixel)
greedy_rect = pg.Rect(pixel, pixel * 2.5, 4 * pixel, pixel)
greedy_settings = [False, False]

dfs_text = font.render('DFS', True, white, None)
dfs_text_rect = dfs_text.get_rect()
dfs_text_rect.center = (8 * pixel, 3 * pixel)
dfs_rect = pg.Rect(6 * pixel, pixel * 2.5, 4 * pixel, pixel)
dfs_settings = [False, False]

bfs_text = font.render('BFS', True, white, None)
bfs_text_rect = bfs_text.get_rect()
bfs_text_rect.center = (13 * pixel, 3 * pixel)
bfs_rect = pg.Rect(11 * pixel, pixel * 2.5, 4 * pixel, pixel)
bfs_settings = [False, False]

a_star_text = font.render('A*', True, white, None)
a_star_text_rect = a_star_text.get_rect()
a_star_text_rect.center = (18 * pixel, 3 * pixel)
a_star_rect = pg.Rect(16 * pixel, pixel * 2.5, 4 * pixel, pixel)
a_star_settings = [False, False]

directions = [
	pg.Vector2(0, 0),
	pg.Vector2(1, 0),
	pg.Vector2(0, -1),
	pg.Vector2(-1, 0),
	pg.Vector2(0, 1),
	pg.Vector2(1, -1),
	pg.Vector2(-1, -1),
	pg.Vector2(-1, 1),
	pg.Vector2(1, 1),
]

class Entity:
	def __init__(self, x, y, color):
		self.anim_position = pg.Vector2(x, y)
		self.last_position = pg.Vector2(x, y)
		self.position = pg.Vector2(x, y)
		self.goal = pg.Vector2(x + 2, y + 2)
		self.color = color

class Wall:
	def __init__(self, x, y):
		self.position = pg.Vector2(x, y)

class Node:
	def __init__(self, positions):
		self.positions = positions
		sum_h = 0
		for i in range(len(positions)):
			sum_h += abs(positions[i].x - goal_positions[i].x) + abs(positions[i].y - goal_positions[i].y)
		self.f = sum_h
		self.h = sum_h
		self.c = 0
		self.expanded = False
		self.parent = []
		for i in range(len(players)):
			self.parent.append(pg.Vector2(-1, -1))

	def set_cost(self, cost):
		self.c = cost
		self.f = self.h + self.c

def add_agent():
	if len(players) == len(player_colors):
		return

	tries = 0
	while tries < 5:
		rx = random.randrange(5, columns - 5)
		ry = random.randrange(5, rows - 5)

		if mapa[int(rx)][int(ry)] == 0:
			players.append(Entity(rx, ry, player_colors[len(players)]))
			return
		tries += 1

	for i in range(len(columns)):
		for j in range(len(rows)):
			if mapa[i][j] == 0:
				players.append(Entity(i, j, player_colors[len(players)]))

def remove_agent():
	if len(players) == 1:
		return

	players.pop(len(players) - 1)

def check_button_hovers(x, y, lclick, onlclick):
	add_settings[0] = False
	add_settings[1] = False

	rem_settings[0] = False
	rem_settings[1] = False

	clear_settings[0] = False
	clear_settings[1] = False

	increase_settings[0] = False
	increase_settings[1] = False

	decrease_settings[0] = False
	decrease_settings[1] = False

	greedy_settings[0] = False
	greedy_settings[1] = False

	dfs_settings[0] = False
	dfs_settings[1] = False

	bfs_settings[0] = False
	bfs_settings[1] = False

	a_star_settings[0] = False
	a_star_settings[1] = False
	
	if search_state[0] != 1 and x >= add_agent_rect.x - 5 and y >= add_agent_rect.y - 5 and x <= add_agent_rect.x + add_agent_rect.w + 5 and y <= add_agent_rect.y + add_agent_rect.h + 5:
		add_settings[0] = True
		add_settings[1] = lclick
		if onlclick:
			add_agent()
			compute_combinations()
	
	if search_state[0] != 1 and x >= rem_agent_rect.x - 5 and y >= rem_agent_rect.y - 5 and x <= rem_agent_rect.x + rem_agent_rect.w + 5 and y <= rem_agent_rect.y + rem_agent_rect.h + 5:
		rem_settings[0] = True
		rem_settings[1] = lclick
		if onlclick:
			remove_agent()
			compute_combinations()
	
	if search_state[0] != 1 and x >= clear_rect.x - 5 and y >= clear_rect.y - 5 and x <= clear_rect.x + clear_rect.w + 5 and y <= clear_rect.y + clear_rect.h + 5:
		clear_settings[0] = True
		clear_settings[1] = lclick
		if onlclick:
			clear_walls()

	if x >= increase_rect.x - 5 and y >= increase_rect.y - 5 and x <= increase_rect.x + increase_rect.w + 5 and y <= increase_rect.y + increase_rect.h + 5:
		increase_settings[0] = True
		increase_settings[1] = lclick
		if onlclick and timeMultiplier[0] < 40:
			timeMultiplier[0] *= 1.5
			speed_text[0] = font.render("{:.1f}%".format(timeMultiplier[0] * 100), True, white, None)
	
	if x >= decrease_rect.x - 5 and y >= decrease_rect.y - 5 and x <= decrease_rect.x + decrease_rect.w + 5 and y <= decrease_rect.y + decrease_rect.h + 5:
		decrease_settings[0] = True
		decrease_settings[1] = lclick
		if onlclick and timeMultiplier[0] > 0.2:
			timeMultiplier[0] /= 1.5
			speed_text[0] = font.render("{:.1f}%".format(timeMultiplier[0] * 100), True, white, None)
	
	if search_state[0] != 1 and x >= greedy_rect.x - 5 and y >= greedy_rect.y - 5 and x <= greedy_rect.x + greedy_rect.w + 5 and y <= greedy_rect.y + greedy_rect.h + 5:
		greedy_settings[0] = True
		greedy_settings[1] = lclick
		if onlclick:
			algorithm[0] = "greedy"
			search[0] = True
	
	if search_state[0] != 1 and x >= dfs_rect.x - 5 and y >= dfs_rect.y - 5 and x <= dfs_rect.x + dfs_rect.w + 5 and y <= dfs_rect.y + dfs_rect.h + 5:
		dfs_settings[0] = True
		dfs_settings[1] = lclick
		if onlclick:
			algorithm[0] = "dfs"
			search[0] = True
	
	if search_state[0] != 1 and x >= bfs_rect.x - 5 and y >= bfs_rect.y - 5 and x <= bfs_rect.x + bfs_rect.w + 5 and y <= bfs_rect.y + bfs_rect.h + 5:
		bfs_settings[0] = True
		bfs_settings[1] = lclick
		if onlclick:
			algorithm[0] = "bfs"
			search[0] = True
	
	if search_state[0] != 1 and x >= a_star_rect.x - 5 and y >= a_star_rect.y - 5 and x <= a_star_rect.x + a_star_rect.w + 5 and y <= a_star_rect.y + a_star_rect.h + 5:
		a_star_settings[0] = True
		a_star_settings[1] = lclick
		if onlclick:
			algorithm[0] = "a_star"
			search[0] = True

def is_empty(x, y):
	return mapa[int(x)][int(y)] == 0

def erase_wall(x, y):
	mapa[int(x)][int(y)] = 0

def clear_walls():
	for i in range(columns):
		for j in range(rows):
			mapa[i][j] = 0

def in_bounds(pos):
	x = int(pos.x)
	y = int(pos.y)
	if x >= 0 and x < columns and y >= 4 and y < rows:
		return True
	return False

def in_bounds_coords(x, y):
	x = int(x)
	y = int(y)
	if x >= 0 and x < columns and y >= 4 and y < rows:
		return True
	return False

def expand(positions):
	gen = []
	for i in range(len(combinations)):
		new_positions = []
		bad_comb = False

		for j in range(len(players)):
			new_position_viewed = pg.Vector2(positions[j].x + combinations[i][j].x, positions[j].y + combinations[i][j].y)
			if not in_bounds(new_position_viewed) or not is_empty(new_position_viewed.x, new_position_viewed.y):
				bad_comb = True
				break
			new_positions.append(new_position_viewed)

		if bad_comb:
			continue

		for j in range(len(players)):
			for k in range(j + 1, len(players), 1):
				if not ((new_positions[j].x != positions[k].x or new_positions[j].y != positions[k].y) and (new_positions[k].x != positions[j].x or new_positions[k].y != positions[j].y) and (new_positions[j].x != new_positions[k].x or new_positions[j].y != new_positions[k].y)):
					bad_comb = True

		if bad_comb:
			continue

		gen.append(new_positions)
	return gen

def compute_combinations():
	combinations.clear()
	if diagonal:
		for i in range(len(directions)):
			compute_child([], i, 1)
	else:
		for i in range(len(directions) - 4):
			compute_child([], i, 1)

def compute_child(comb_arr, dir, depth):
	comb_arr.append(directions[dir])
	if depth == len(players):
		combinations.append(comb_arr.copy())
	elif diagonal:
		for i in range(len(directions)):
			compute_child(comb_arr, i, depth + 1)
	else:
		for i in range(len(directions) - 4):
			compute_child(comb_arr, i, depth + 1)
	comb_arr.pop(len(comb_arr) - 1)

def track_path(src):
	arr = []
	parent_different = False
	for i in range(len(players)):
		if src.parent[i].x != -1 or src.parent[i].y != -1:
			parent_different = True
			break

	while parent_different:
		arr.append(src)

		for i in range(len(expanded_nodes)):
			end = True
			for j in range(len(players)):
				if src.parent[j].x != expanded_nodes[i].positions[j].x or src.parent[j].y != expanded_nodes[i].positions[j].y:
					end = False
					break
			if end:
				src = expanded_nodes[i]
				break

		parent_different = False
		for i in range(len(players)):
			if src.parent[i].x != -1 or src.parent[i].y != -1:
				parent_different = True
				break
	return arr

def dfs(start_positions):
	start_node = Node(start_positions)

	gen_nodes = {}
	expanded_nodes.clear()

	#para dfs la frontera funciona como stack
	frontier = []
	frontier.append(start_node)

	while len(frontier) > 0:
		current = frontier[len(frontier) - 1]
			
		current.expanded = True
		expanded_nodes.append(current)

		if current.h == 0:
			search_state[0] = 1
			return track_path(current)

		gen = expand(current.positions)

		#quita de la lista aquellos nodos previamente generados
		i = 0
		while i < len(gen):
			key = construct_key(gen[i])
			if key in gen_nodes.keys():
				gen.pop(i)
				i -= 1
			i += 1

		frontier.pop(len(frontier) - 1)

		for i in range(len(gen) - 1, -1, -1):
			key = construct_key(gen[i])
			gen_nodes[key] = True
			node = Node(gen[i])
			node.parent = current.positions
			frontier.append(node)

	search_state[0] = 2
	return []

def bfs(start_positions):
	start_node = Node(start_positions)

	gen_nodes = {}
	expanded_nodes.clear()
	frontier = []
	frontier.append(start_node)

	while len(frontier) > 0:
		new_frontier = []

		for p in range(len(frontier)):
			frontier[p].expanded = True
			expanded_nodes.append(frontier[p])

			if frontier[p].h == 0:
				search_state[0] = 1
				return track_path(frontier[p])
			
			gen = expand(frontier[p].positions)

			#quita de la lista aquellos nodos previamente generados
			i = 0
			while i < len(gen):
				key = construct_key(gen[i])
				if key in gen_nodes.keys():
					gen.pop(i)
					i -= 1
				i += 1

			for i in range(len(gen)):
				key = construct_key(gen[i])
				gen_nodes[key] = True
				node = Node(gen[i])
				node.parent = frontier[p].positions
				new_frontier.append(node)

		frontier = new_frontier

	search_state[0] = 2
	return []

def a_star(start_positions):
	start_node = Node(start_positions)

	viewed_nodes.clear()
	expanded_nodes.clear()
	frontier = []
	frontier.append(start_node)
	
	#itera mientras existan nodos en la frontera
	while len(frontier) > 0:

		#se hace la busqueda del mejor nodo: esto es, mínima heurística + costo
		best = frontier[0]
		best_index = 0
		for i in range(1, len(frontier)):
			if frontier[i].f < best.f or (frontier[i].f == best.f and frontier[i].h < best.h):
				best = frontier[i]
				best_index = i

		best.expanded = True
		expanded_nodes.append(best)

		if best.h == 0:
			search_state[0] = 1
			return track_path(best)

		gen = expand(best.positions)

		for i in range(len(gen)):
			key = construct_key(gen[i])
			if key in viewed_nodes.keys() and viewed_nodes[key].expanded:
				continue

			extra_cost = 1
			for j in range(len(players)):
				if gen[i][j].x == best.positions[j].x and gen[i][j].y == best.positions[j].y and (gen[i][j].x != goal_positions[j].x or gen[i][j].y != goal_positions[j].y):
					extra_cost += 0.01

			if not key in viewed_nodes.keys():
				node = Node(gen[i])
				node.parent = best.positions
				node.set_cost(best.c + extra_cost)
				node.parent = best.positions
				viewed_nodes[key] = node
				frontier.append(node)
			else:
				node = viewed_nodes[key]
				if best.c + extra_cost < node.c:
					node.set_cost(best.c + extra_cost)
					node.parent = best.positions

		frontier.pop(best_index)

	search_state[0] = 2
	return []

def greedy(start_positions):
	start_node = Node(start_positions)

	gen_nodes = {}
	expanded_nodes.clear()
	frontier = []
	frontier.append(start_node)

	#itera mientras existan nodos en la frontera
	while len(frontier) > 0:
		#se hace la busqueda del mejor nodo: esto es, mínima heurística + costo
		best = frontier[0]
		best_index = 0
		for i in range(1, len(frontier)):
			if frontier[i].h < best.h:
				best = frontier[i]
				best_index = i

		best.expanded = True
		expanded_nodes.append(best)

		if best.h == 0:
			search_state[0] = 1
			return track_path(best)
 
		gen = expand(best.positions)

		for i in range(len(gen)):
			key = construct_key(gen[i])
			if key in gen_nodes.keys():
				continue
			gen_nodes[key] = True
			node = Node(gen[i])
			node.parent = best.positions
			frontier.append(node)

		frontier.pop(best_index)

	search_state[0] = 2
	return []

def construct_key(positions):
	k = ""
	for i in range(len(positions)):
		k += str(int(positions[i].x)) + str(int(positions[i].y))
	return k

def greedy_old(start_positions):
	start_node = Node(start_positions)

	expanded_nodes.clear()
	frontier = []
	frontier.append(start_node)

	#itera mientras existan nodos en la frontera
	while len(frontier) > 0:
		#se hace la busqueda del mejor nodo: esto es, mínima heurística + costo
		best = frontier[0]
		best_index = 0
		for i in range(1, len(frontier)):
			if frontier[i].h < best.h:
				best = frontier[i]
				best_index = i

		best.expanded = True
		expanded_nodes.append(best)

		if best.h == 0:
			search_state[0] = 1
			return track_path(best)
 
		gen = expand(best.positions)

		for i in range(len(gen)):
			step = False
			for j in range(len(frontier)):
				if frontier[j].positions == gen[i]:
					step = True
					break
			if not step:
				for j in range(len(expanded_nodes)):
					if expanded_nodes[j].positions == gen[i]:
						step = True
						break
			if step:
				continue
			node = Node(gen[i])
			node.generated = True
			node.parent = best.positions
			frontier.append(node)

		frontier.pop(best_index)

	search_state[0] = 2
	return []

def start(src, search):
	if search == "greedy":
		return greedy(src)
	elif search == "dfs":
		return dfs(src)
	elif search == "bfs":
		return bfs(src)
	elif search == "a_star":
		return a_star(src)
	return []
 
def ease_lerp(x):
	ret = 1 - (x * x)
	return ret

def draw():
	surface.fill(bg_primary)

	for i in range(columns):
		for j in range(4, rows, 1):
			if (i >= 0 and i < columns and j >= 0 and j < rows and mapa[i][j] == 1):
				pg.draw.rect(surface, black, pg.Rect(i * pixel, j * pixel, pixel, pixel), 0)
			elif (i + j) % 2 == 1:
				pg.draw.rect(surface, bg_secondary, pg.Rect(i * pixel, j * pixel, pixel, pixel), 0)

	for i in range(len(players)):
		pg.draw.rect(surface, players[i].color, pg.Rect(players[i].goal.x * pixel, players[i].goal.y * pixel, pixel, pixel), 5)
	for i in range(len(players)):
		pg.draw.rect(surface, players[i].color, pg.Rect(players[i].anim_position.x * pixel, players[i].anim_position.y * pixel, pixel, pixel), 0)

	if add_settings[1]:
		pg.draw.rect(surface, bg_secondary, pg.Rect(add_agent_rect.x - 5, add_agent_rect.y - 5, add_agent_rect.w + 10, add_agent_rect.h + 10), 5)
		pg.draw.rect(surface, white, pg.Rect(add_agent_rect.x - 7, add_agent_rect.y - 7, add_agent_rect.w + 14, add_agent_rect.h + 14), 5)
	elif add_settings[0]:
		pg.draw.rect(surface, bg_secondary, pg.Rect(add_agent_rect.x - 5, add_agent_rect.y - 5, add_agent_rect.w + 10, add_agent_rect.h + 10), 5)
		pg.draw.rect(surface, white, pg.Rect(add_agent_rect.x - 10, add_agent_rect.y - 10, add_agent_rect.w + 20, add_agent_rect.h + 20), 5)
	else:
		pg.draw.rect(surface, bg_secondary, pg.Rect(add_agent_rect.x - 5, add_agent_rect.y - 5, add_agent_rect.w + 10, add_agent_rect.h + 10), 5)
	surface.blit(add_agent_text, add_agent_text_rect)

	if rem_settings[1]:
		pg.draw.rect(surface, bg_secondary, pg.Rect(rem_agent_rect.x - 5, rem_agent_rect.y - 5, rem_agent_rect.w + 10, rem_agent_rect.h + 10), 5)
		pg.draw.rect(surface, white, pg.Rect(rem_agent_rect.x - 7, rem_agent_rect.y - 7, rem_agent_rect.w + 14, rem_agent_rect.h + 14), 5)
	elif rem_settings[0]:
		pg.draw.rect(surface, bg_secondary, pg.Rect(rem_agent_rect.x - 5, rem_agent_rect.y - 5, rem_agent_rect.w + 10, rem_agent_rect.h + 10), 5)
		pg.draw.rect(surface, white, pg.Rect(rem_agent_rect.x - 10, rem_agent_rect.y - 10, rem_agent_rect.w + 20, rem_agent_rect.h + 20), 5)
	else:
		pg.draw.rect(surface, bg_secondary, pg.Rect(rem_agent_rect.x - 5, rem_agent_rect.y - 5, rem_agent_rect.w + 10, rem_agent_rect.h + 10), 5)
	surface.blit(rem_agent_text, rem_agent_text_rect)

	if clear_settings[1]:
		pg.draw.rect(surface, bg_secondary, pg.Rect(clear_rect.x - 5, clear_rect.y - 5, clear_rect.w + 10, clear_rect.h + 10), 5)
		pg.draw.rect(surface, white, pg.Rect(clear_rect.x - 7, clear_rect.y - 7, clear_rect.w + 14, clear_rect.h + 14), 5)
	elif clear_settings[0]:
		pg.draw.rect(surface, bg_secondary, pg.Rect(clear_rect.x - 5, clear_rect.y - 5, clear_rect.w + 10, clear_rect.h + 10), 5)
		pg.draw.rect(surface, white, pg.Rect(clear_rect.x - 10, clear_rect.y - 10, clear_rect.w + 20, clear_rect.h + 20), 5)
	else:
		pg.draw.rect(surface, bg_secondary, pg.Rect(clear_rect.x - 5, clear_rect.y - 5, clear_rect.w + 10, clear_rect.h + 10), 5)
	surface.blit(clear_text, clear_text_rect)

	if increase_settings[1]:
		pg.draw.rect(surface, bg_secondary, pg.Rect(increase_rect.x - 5, increase_rect.y - 5, increase_rect.w + 10, increase_rect.h + 10), 5)
		pg.draw.rect(surface, white, pg.Rect(increase_rect.x - 7, increase_rect.y - 7, increase_rect.w + 14, increase_rect.h + 14), 5)
	elif increase_settings[0]:
		pg.draw.rect(surface, bg_secondary, pg.Rect(increase_rect.x - 5, increase_rect.y - 5, increase_rect.w + 10, increase_rect.h + 10), 5)
		pg.draw.rect(surface, white, pg.Rect(increase_rect.x - 10, increase_rect.y - 10, increase_rect.w + 20, increase_rect.h + 20), 5)
	else:
		pg.draw.rect(surface, bg_secondary, pg.Rect(increase_rect.x - 5, increase_rect.y - 5, increase_rect.w + 10, increase_rect.h + 10), 5)
	surface.blit(increase_text, increase_text_rect)

	if decrease_settings[1]:
		pg.draw.rect(surface, bg_secondary, pg.Rect(decrease_rect.x - 5, decrease_rect.y - 5, decrease_rect.w + 10, decrease_rect.h + 10), 5)
		pg.draw.rect(surface, white, pg.Rect(decrease_rect.x - 7, decrease_rect.y - 7, decrease_rect.w + 14, decrease_rect.h + 14), 5)
	elif decrease_settings[0]:
		pg.draw.rect(surface, bg_secondary, pg.Rect(decrease_rect.x - 5, decrease_rect.y - 5, decrease_rect.w + 10, decrease_rect.h + 10), 5)
		pg.draw.rect(surface, white, pg.Rect(decrease_rect.x - 10, decrease_rect.y - 10, decrease_rect.w + 20, decrease_rect.h + 20), 5)
	else:
		pg.draw.rect(surface, bg_secondary, pg.Rect(decrease_rect.x - 5, decrease_rect.y - 5, decrease_rect.w + 10, decrease_rect.h + 10), 5)
	surface.blit(decrease_text, decrease_text_rect)

	surface.blit(speed_text[0], speed_text_rect)
	surface.blit(state_text[0], state_text_rect)

	if greedy_settings[1]:
		pg.draw.rect(surface, bg_secondary, pg.Rect(greedy_rect.x - 5, greedy_rect.y - 5, greedy_rect.w + 10, greedy_rect.h + 10), 5)
		pg.draw.rect(surface, white, pg.Rect(greedy_rect.x - 7, greedy_rect.y - 7, greedy_rect.w + 14, greedy_rect.h + 14), 5)
	elif greedy_settings[0]:
		pg.draw.rect(surface, bg_secondary, pg.Rect(greedy_rect.x - 5, greedy_rect.y - 5, greedy_rect.w + 10, greedy_rect.h + 10), 5)
		pg.draw.rect(surface, white, pg.Rect(greedy_rect.x - 10, greedy_rect.y - 10, greedy_rect.w + 20, greedy_rect.h + 20), 5)
	else:
		pg.draw.rect(surface, bg_secondary, pg.Rect(greedy_rect.x - 5, greedy_rect.y - 5, greedy_rect.w + 10, greedy_rect.h + 10), 5)
	surface.blit(greedy_text, greedy_text_rect)

	if dfs_settings[1]:
		pg.draw.rect(surface, bg_secondary, pg.Rect(dfs_rect.x - 5, dfs_rect.y - 5, dfs_rect.w + 10, dfs_rect.h + 10), 5)
		pg.draw.rect(surface, white, pg.Rect(dfs_rect.x - 7, dfs_rect.y - 7, dfs_rect.w + 14, dfs_rect.h + 14), 5)
	elif dfs_settings[0]:
		pg.draw.rect(surface, bg_secondary, pg.Rect(dfs_rect.x - 5, dfs_rect.y - 5, dfs_rect.w + 10, dfs_rect.h + 10), 5)
		pg.draw.rect(surface, white, pg.Rect(dfs_rect.x - 10, dfs_rect.y - 10, dfs_rect.w + 20, dfs_rect.h + 20), 5)
	else:
		pg.draw.rect(surface, bg_secondary, pg.Rect(dfs_rect.x - 5, dfs_rect.y - 5, dfs_rect.w + 10, dfs_rect.h + 10), 5)
	surface.blit(dfs_text, dfs_text_rect)

	if bfs_settings[1]:
		pg.draw.rect(surface, bg_secondary, pg.Rect(bfs_rect.x - 5, bfs_rect.y - 5, bfs_rect.w + 10, bfs_rect.h + 10), 5)
		pg.draw.rect(surface, white, pg.Rect(bfs_rect.x - 7, bfs_rect.y - 7, bfs_rect.w + 14, bfs_rect.h + 14), 5)
	elif bfs_settings[0]:
		pg.draw.rect(surface, bg_secondary, pg.Rect(bfs_rect.x - 5, bfs_rect.y - 5, bfs_rect.w + 10, bfs_rect.h + 10), 5)
		pg.draw.rect(surface, white, pg.Rect(bfs_rect.x - 10, bfs_rect.y - 10, bfs_rect.w + 20, bfs_rect.h + 20), 5)
	else:
		pg.draw.rect(surface, bg_secondary, pg.Rect(bfs_rect.x - 5, bfs_rect.y - 5, bfs_rect.w + 10, bfs_rect.h + 10), 5)
	surface.blit(bfs_text, bfs_text_rect)

	if a_star_settings[1]:
		pg.draw.rect(surface, bg_secondary, pg.Rect(a_star_rect.x - 5, a_star_rect.y - 5, a_star_rect.w + 10, a_star_rect.h + 10), 5)
		pg.draw.rect(surface, white, pg.Rect(a_star_rect.x - 7, a_star_rect.y - 7, a_star_rect.w + 14, a_star_rect.h + 14), 5)
	elif a_star_settings[0]:
		pg.draw.rect(surface, bg_secondary, pg.Rect(a_star_rect.x - 5, a_star_rect.y - 5, a_star_rect.w + 10, a_star_rect.h + 10), 5)
		pg.draw.rect(surface, white, pg.Rect(a_star_rect.x - 10, a_star_rect.y - 10, a_star_rect.w + 20, a_star_rect.h + 20), 5)
	else:
		pg.draw.rect(surface, bg_secondary, pg.Rect(a_star_rect.x - 5, a_star_rect.y - 5, a_star_rect.w + 10, a_star_rect.h + 10), 5)
	surface.blit(a_star_text, a_star_text_rect)

	pg.display.update()

if __name__ == "__main__":
	players.append(Entity(10, 10, red))
	compute_combinations()

	for i in range(columns):
		mapa.append([])
		for j in range(rows):
			mapa[i].append(0)

	while run:
		for event in pg.event.get():
			if event.type == pg.QUIT:
				run = False

		keys = pg.key.get_pressed()
		[mouse_x, mouse_y] = mouse.get_pos()

		left_onpress = not left_click
		left_click = mouse.get_pressed(3)[0]
		left_onpress = left_onpress and left_click
		right_click = mouse.get_pressed(3)[2]

		if (left_click or right_click) and search_state[0] == 2:
			search_state[0] = 0
			state = "Idle"
			state_color[0] = white
			state_text[0] = font.render(state, True, state_color[0], None)

		check_button_hovers(mouse_x, mouse_y, left_click, left_onpress)

		if search_state[0] != 1:
			if left_click:
				mx = int(mouse_x / pixel)
				my = int(mouse_y / pixel)
				if dragging:
					if player_dragged != -1 and in_bounds_coords(mx, my):
						players[player_dragged].position = pg.Vector2(mx, my)
					elif goal_dragged != -1 and in_bounds_coords(mx, my):
						players[goal_dragged].goal = pg.Vector2(mx, my)
				elif left_onpress:
					for i in range(len(players)):
						if mx == players[i].position.x and my == players[i].position.y:
							position_dragged = players[i].position
							player_dragged = i
							goal_dragged = -1
							dragging = True
						elif mx == players[i].goal.x and my == players[i].goal.y:
							player_dragged = -1
							goal_dragged = i
							dragging = True
				if not dragging and in_bounds_coords(mx, my) and is_empty(mx, my):
					mapa[int(mx)][int(my)] = 1
			elif dragging:
				dragging = False

			if right_click:
				mx = int(mouse_x / pixel)
				my = int(mouse_y / pixel)
				if in_bounds_coords(mx, my):
					mapa[int(mx)][int(my)] = 0

			if keys[pg.K_1]:
				algorithm = "greedy"
				search[0] = True
			elif keys[pg.K_2]:
				algorithm = "dfs"
				search[0] = True
			elif keys[pg.K_3]:
				algorithm = "bfs"
				search[0] = True
			elif keys[pg.K_4]:
				algorithm = "a_star"
				search[0] = True

			if search[0] and not pressing:
				goal_positions.clear()
				init_positions.clear()
				for i in range(len(players)):
					goal_positions.append(players[i].goal)
					init_positions.append(players[i].position)
				state = "Computing..."
				state_color[0] = 255, 138, 61
				state_text[0] = font.render(state, True, state_color[0], None)
				draw()

				moves.clear()
				moves += start(init_positions, algorithm[0])
				algorithm[0] = ""
				search[0] = False

				if search_state[0] == 1:
					state = "Path was found!"
					state_color[0] = green
					state_text[0] = font.render(state, True, state_color[0], None)
				elif search_state[0] == 2:
					state = "Path not found"
					state_color[0] = red
					state_text[0] = font.render(state, True, state_color[0], None)
				pressing = True
			elif not search[0]:
				pressing = False

		if cooldown > 0:
			cooldown -= 0.008 * timeMultiplier[0]
		elif cooldown < 0:
			cooldown = 0

		normalized_cooldown = cooldown / defaultCooldown

		for i in range(len(players)):
			players[i].anim_position = (players[i].last_position + (players[i].position - players[i].last_position) * ease_lerp(normalized_cooldown))

		if cooldown == 0 and len(moves) > 0:
			new_positions = moves[len(moves) - 1]
			for i in range(len(players)):
				players[i].last_position.x = players[i].position.x
				players[i].last_position.y = players[i].position.y
				players[i].position.x = new_positions.positions[i].x
				players[i].position.y = new_positions.positions[i].y
			cooldown = defaultCooldown
			moves.pop(len(moves) - 1)
		elif cooldown == 0 and search_state[0] == 1:
			search_state[0] = 0
			state = "Idle"
			state_color[0] = white
			state_text[0] = font.render(state, True, state_color[0], None)

		draw()
		deltaTime = clock.tick_busy_loop(framerate) / 1000.0
		pg.display.set_caption("IA project - FPS: " + str(int(clock.get_fps())))

	pg.quit()