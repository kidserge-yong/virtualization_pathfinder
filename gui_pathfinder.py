import pygame
import pygame_menu
import math
from queue import PriorityQueue

WIDTH = 800
ROWS_SIZE = 50

diagonal_motion = [True]
verhor_g = [1.0]
diagonal_g = [1.4]
step = [False]


RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 255, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165 ,0)
GREY = (128, 128, 128)
TURQUOISE = (64, 224, 208)


class Spot:

	def __init__(self, row, col, width, total_rows, is_allow_diagonal):
		self.row = row
		self.col = col
		self.x = row * width
		self.y = col * width
		self.color = WHITE
		self.neighbors = []
		self.width = width
		self.total_rows = total_rows
		self.is_allow_diagonal = is_allow_diagonal

	def get_pos(self):
		return self.row, self.col

	def is_closed(self):
		return self.color == RED

	def is_open(self):
		return self.color == GREEN

	def is_barrier(self):
		return self.color == BLACK

	def is_start(self):
		return self.color == ORANGE

	def is_end(self):
		return self.color == TURQUOISE

	def reset(self):
		self.color = WHITE

	def make_start(self):
		self.color = ORANGE

	def make_closed(self):
		self.color = RED

	def make_open(self):
		self.color = GREEN

	def make_barrier(self):
		self.color = BLACK

	def make_end(self):
		self.color = TURQUOISE

	def make_path(self):
		self.color = PURPLE

	def draw(self, win):
		pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))

	def update_neighbors(self, grid):
		self.neighbors = []
		if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_barrier(): # DOWN
			self.neighbors.append(grid[self.row + 1][self.col])

		if self.row > 0 and not grid[self.row - 1][self.col].is_barrier(): # UP
			self.neighbors.append(grid[self.row - 1][self.col])

		if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_barrier(): # RIGHT
			self.neighbors.append(grid[self.row][self.col + 1])

		if self.col > 0 and not grid[self.row][self.col - 1].is_barrier(): # LEFT
			self.neighbors.append(grid[self.row][self.col - 1])

		if not self.is_allow_diagonal: return

		if self.row < self.total_rows - 1 and self.col < self.total_rows - 1 and not grid[self.row + 1][self.col + 1].is_barrier(): #DOWN RIGHT
			self.neighbors.append(grid[self.row + 1][self.col + 1])
		
		if self.row < self.total_rows - 1 and self.col > 0 and not grid[self.row + 1][self.col - 1].is_barrier(): #DOWN LEFT
			self.neighbors.append(grid[self.row + 1][self.col - 1])
		
		if self.row > 0 and self.col < self.total_rows - 1 and not grid[self.row - 1][self.col + 1].is_barrier(): #UP RIGHT
			self.neighbors.append(grid[self.row - 1][self.col + 1])
		
		if self.row > 0 and self.col > 0 and not grid[self.row - 1][self.col - 1].is_barrier(): #UP LEFT
			self.neighbors.append(grid[self.row - 1][self.col - 1])


	def __lt__(self, other):
		return False


def h(p1, p2):
	x1, y1 = p1
	x2, y2 = p2
	return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)


def reconstruct_path(came_from, current, draw):
	while current in came_from:
		current = came_from[current]
		current.make_path()
		draw()

def wait():
	while True:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				exit()
			if pygame.mouse.get_pressed()[0]:
				return True
			if pygame.mouse.get_pressed()[2]:
				return False
				

def algorithm_Astar(draw, grid, start, end, config):

	is_allow_diagonal = config[0][0]
	verti_horiz_g = config[1][0]
	diagonal_g = config[2][0]
	is_wait = config[3][0]

	#print(config)

	count = 0
	open_set = PriorityQueue()
	open_set.put((0, count, start))
	came_from = {}
	g_score = {spot: float("inf") for row in grid for spot in row}
	g_score[start] = 0
	f_score = {spot: float("inf") for row in grid for spot in row}
	f_score[start] = h(start.get_pos(), end.get_pos())

	open_set_hash = {start}


	while not open_set.empty():
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				exit()

		current = open_set.get()[2]
		open_set_hash.remove(current)

		if current == end:
			reconstruct_path(came_from, end, draw)
			end.make_end()
			start.make_start()
			return True

		neighbor_count = 0
		for neighbor in current.neighbors:
			if neighbor_count < 4:
				temp_g_score = g_score[current] + verti_horiz_g
			else:
				temp_g_score = g_score[current] + diagonal_g
			neighbor_count+=1

			if temp_g_score < g_score[neighbor]:
				came_from[neighbor] = current
				g_score[neighbor] = temp_g_score
				f_score[neighbor] = temp_g_score + h(neighbor.get_pos(), end.get_pos())
				if neighbor not in open_set_hash and not neighbor.is_closed():
					count += 1
					open_set.put((f_score[neighbor], count, neighbor))
					open_set_hash.add(neighbor)
					neighbor.make_open()

		draw()
		
		if is_wait:
			is_wait = wait()

		if current != start:
			current.make_closed()

	return False

def algorithm_BFS(draw, grid, start, end, config):
	import queue

	is_allow_diagonal = config[0][0]
	verti_horiz_g = config[1][0]
	diagonal_g = config[2][0]
	is_wait = config[3][0]


	came_from = {}
	open_queue = queue.Queue()
	open_queue.put(start)
	current = start

	while not open_queue.empty():
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				exit()

		if current == end:
			reconstruct_path(came_from, end, draw)
			end.make_end()
			start.make_start()
			return True

		current = open_queue.get()
		if current.is_closed():
			continue
		for neighbor in current.neighbors:
			if not neighbor.is_closed() and not neighbor.is_start():
				came_from[neighbor] = current
				open_queue.put(neighbor)
				neighbor.make_open()

		draw()
		
		if is_wait:
			is_wait = wait()

		if current != start:
			current.make_closed()


def make_grid(rows, width, is_allow_diagonal):
	grid = []
	gap = width // rows
	for i in range(rows):
		grid.append([])
		for j in range(rows):
			spot = Spot(i, j, gap, rows, is_allow_diagonal)
			grid[i].append(spot)

	return grid


def draw_grid(win, rows, width):
	gap = width // rows
	for i in range(rows):
		pygame.draw.line(win, GREY, (0, i * gap), (width, i * gap))
		for j in range(rows):
			pygame.draw.line(win, GREY, (j * gap, 0), (j * gap, width))


def draw(win, grid, rows, width):
	win.fill(WHITE)

	for row in grid:
		for spot in row:
			spot.draw(win)

	draw_grid(win, rows, width)
	pygame.display.update()


def get_clicked_pos(pos, rows, width):
	gap = width // rows
	y, x = pos

	row = y // gap
	col = x // gap

	return row, col


def play_function(win, width, config):
	is_allow_diagonal = config[0][0]
	algorithm = config[4][0]

	ROWS = ROWS_SIZE
	grid = make_grid(ROWS, width, is_allow_diagonal)

	start = None
	end = None

	run = True
	while run:
		draw(win, grid, ROWS, width)
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False

			if pygame.mouse.get_pressed()[0]: # LEFT
				pos = pygame.mouse.get_pos()
				row, col = get_clicked_pos(pos, ROWS, width)
				spot = grid[row][col]
				if not start and spot != end:
					start = spot
					start.make_start()

				elif not end and spot != start:
					end = spot
					end.make_end()

				elif spot != end and spot != start:
					spot.make_barrier()

			elif pygame.mouse.get_pressed()[1]: # MIDDLE
				start = None
				end = None
				grid = make_grid(ROWS, width, is_allow_diagonal)

			elif pygame.mouse.get_pressed()[2]: # RIGHT
				pos = pygame.mouse.get_pos()
				row, col = get_clicked_pos(pos, ROWS, width)
				spot = grid[row][col]
				spot.reset()
				if spot == start:
					start = None
				elif spot == end:
					end = None

			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_SPACE and start and end:
					for row in grid:
						for spot in row:
							spot.update_neighbors(grid)

					algorithm(lambda: draw(win, grid, ROWS, width), grid, start, end, config)

				elif event.key == pygame.K_r:
					main()

										

	pygame.quit()
	exit()


algorithm = [algorithm_Astar]

def main(test=False):
	"""
	Main program.
	:param test: Indicate function is being tested
	:type test: bool
	:return: None
	"""

	# -------------------------------------------------------------------------
	# Globals
	# -------------------------------------------------------------------------
	#global IS_ALLOW_DIAGONAL
	#global DIAGONAL_G_VALUE
	#global VERTI_HORIZ_G_VALUE

	# -------------------------------------------------------------------------
    # Init pygame
    # -------------------------------------------------------------------------
	pygame.init()
	surface = pygame.display.set_mode((WIDTH, WIDTH))
	pygame.display.set_caption("Path Finding Algorithm")


	# -------------------------------------------------------------------------
    # Create menus: Main
    # -------------------------------------------------------------------------

	def set_verhor_g(value):
		try:
			verhor_g[0] = float(value)
		except ValueError:
			print("ERROR: Please enter number in float")
			pass

	def set_diagonal_g(value):
		try:
			diagonal_g[0] = float(value)
		except ValueError:
			print("ERROR: Please enter number in float")
			pass

	def set_diagonal_motion(text, value):
		diagonal_motion[0] = value

	def set_algorithm(text, value):
		algorithm[0] = value

	def set_step(text, value):
		step[0] = value

	def start_the_game(WIN, value, config):
		#print(config)
		play_function(WIN, WIDTH, config)


	menu = pygame_menu.Menu(600, 600, 'Welcome',
						theme=pygame_menu.themes.THEME_BLUE)

	menu.add_selector('Algorithm :',
						[('A*', algorithm_Astar),
						('Breadth First Search (BFS)', algorithm_BFS)],
						onchange=set_algorithm
						)
	menu.add_text_input('Vertical G value :', 
						default = str(verhor_g[0]), 
						onchange=set_verhor_g
						)
	menu.add_selector('Enable Diagonal Motion: ', 
						[('Yes', True), 
						('No', False)], 
						onchange=set_diagonal_motion
						)
	menu.add_text_input('Diagonal G value :', 
						default = str(diagonal_g[0]), 
						onchange=set_diagonal_g
						)

	menu.add_selector('Enable step : ', 
						[('No', False),
						('Yes', True)
						], 
						onchange=set_step
						)

	menu.add_button('Play', 
					start_the_game, 
					surface, 
					WIDTH, 
					(diagonal_motion, verhor_g, diagonal_g, step, algorithm))
	menu.add_button('Quit', pygame_menu.events.EXIT)

	menu.mainloop(surface)


if __name__ == '__main__':
    main()



##if IS_ALLOW_DIAGONAL:
#	menu.add_text_input('Diagonal G value :', default = '1', onchange=set_diagonal_g)
#menu.add_button('Play', main(WIN, WIDTH))












