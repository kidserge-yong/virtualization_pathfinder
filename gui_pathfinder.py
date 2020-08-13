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
	"""
	Object represent each block on the screen

	Parameters:
    row (int): row of the block
	collumn (int): collumn of the block
	width (int): size of row and collumn (in pixel), This case we use .rec. Therefore should be the same
	total_rows (int): total number of rows

    Returns:
    None
	"""

	def __init__(self, row, col, width, total_rows):
		self.row = row
		self.col = col
		self.x = row * width
		self.y = col * width
		self.color = WHITE
		self.neighbors = []
		self.width = width
		self.total_rows = total_rows

	def get_pos(self):
		"""
		Returns:
		:row (int), collumn (int): position of that spot
		"""
		return self.row, self.col

	def is_closed(self):
		"""
		Returns:
		True if the spot already make_close()
		"""
		return self.color == RED

	def is_open(self):
		"""
		Returns:
		True if the spot already make_open()
		"""
		return self.color == GREEN

	def is_barrier(self):
		"""
		Returns:
		True if the spot already make_barrier()
		"""
		return self.color == BLACK

	def is_start(self):
		"""
		Returns:
		True if the spot already make_start()
		"""
		return self.color == ORANGE

	def is_end(self):
		"""
		Returns:
		True if the spot already make_end()
		"""
		return self.color == TURQUOISE

	def is_path(self):
		"""
		Returns:
		True if the spot already make_path()
		"""
		return self.color == PURPLE

	def reset(self):
		"""
		Return to initial state of spot
		"""
		self.color = WHITE

	def make_start(self):
		"""
		Make spot to be start spot
		"""
		self.color = ORANGE

	def make_closed(self):
		"""
		Make spot to be closed spot
		"""
		self.color = RED

	def make_open(self):
		"""
		Make spot to be open spot
		"""
		self.color = GREEN

	def make_barrier(self):
		"""
		Make spot to be barrier (cannot pass)
		"""
		self.color = BLACK

	def make_end(self):
		"""
		Make spot to be end (cannot pass)
		"""
		self.color = TURQUOISE

	def make_path(self):
		"""
		Make spot to path from start to end
		"""
		self.color = PURPLE

	def draw(self, win):
		"""
		Draw color of spot
		:win (pygame Surface): https://www.pygame.org/docs/ref/surface.html#:~:text=A%20pygame%20Surface%20is%20used,create%20a%20new%20image%20object.
		"""
		pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))

	def update_neighbors(self, grid, is_allow_diagonal):
		"""
		Connect spot to neighbors spot

		:grid (List[int][int]: Spot): grid is 2D array of spot
		:is_allow_diagonal (bool): controller for neighbors

		:return: None
		"""
		self.neighbors = []
		if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_barrier(): # DOWN
			self.neighbors.append(grid[self.row + 1][self.col])

		if self.row > 0 and not grid[self.row - 1][self.col].is_barrier(): # UP
			self.neighbors.append(grid[self.row - 1][self.col])

		if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_barrier(): # RIGHT
			self.neighbors.append(grid[self.row][self.col + 1])

		if self.col > 0 and not grid[self.row][self.col - 1].is_barrier(): # LEFT
			self.neighbors.append(grid[self.row][self.col - 1])

		if not is_allow_diagonal: return

		if self.row < self.total_rows - 1 and self.col < self.total_rows - 1 and not grid[self.row + 1][self.col + 1].is_barrier(): #DOWN RIGHT
			self.neighbors.append(grid[self.row + 1][self.col + 1])
		
		if self.row < self.total_rows - 1 and self.col > 0 and not grid[self.row + 1][self.col - 1].is_barrier(): #DOWN LEFT
			self.neighbors.append(grid[self.row + 1][self.col - 1])
		
		if self.row > 0 and self.col < self.total_rows - 1 and not grid[self.row - 1][self.col + 1].is_barrier(): #UP RIGHT
			self.neighbors.append(grid[self.row - 1][self.col + 1])
		
		if self.row > 0 and self.col > 0 and not grid[self.row - 1][self.col - 1].is_barrier(): #UP LEFT
			self.neighbors.append(grid[self.row - 1][self.col - 1])


	def __lt__(self, other):
		"""
		Less than function when compare spot with spot
		:other (Spot): the spot we want to compare.

		:return: None
		"""
		return False


def h(p1, p2):
	"""
	h value function, find distance between 2 spots
	:p1 (Spot): first spot
	:p2 (Spot): second spot (conventionally end)

	:return: None
	"""
	x1, y1 = p1
	x2, y2 = p2
	#return abs(x1 - x2) + abs(y1 - y2)
	return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)


def reconstruct_path(came_from, current, draw):
	"""
	track back using list of spot in came_from
	:came_from (list[Spot]:Spot): list of spot represent path from start to end
	:current (Spot): initial spot to track back to start spot
	:draw (lambda: draw): draw every spot and update the pygame screen
	
	:return: None
	"""
	while current in came_from:
		current = came_from[current]
		current.make_path()
		draw()

def wait():
	"""
	Wait function to control step of program usign event handle in pygame
	
	:return: None
	"""
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
	"""
	Path finding A* algorithm
	:draw (lambda: draw): draw every spot and update the pygame screen
	:grid (List[int][int]: Spot): grid is 2D array of spot
	:start (Spot): start spot
	:end (Spot): end spot
	:config (List[][]): detail configuration from pymenu

	:return: None
	"""

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
	"""
	Path finding Breadth-first search algorithm
	:draw (lambda: draw): draw every spot and update the pygame screen
	:grid (List[int][int]: Spot): grid is 2D array of spot
	:start (Spot): start spot
	:end (Spot): end spot
	:config (List[][]): detail configuration from pymenu

	:return: None
	"""
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


def make_grid(rows, width):
	"""
	Create Spot object into from rows and width data
	:rows (int): number of rows and collumn needed
	:width (int): size of width in pixel

	:return: None
	"""
	grid = []
	gap = width // rows
	for i in range(rows):
		grid.append([])
		for j in range(rows):
			spot = Spot(i, j, gap, rows)
			grid[i].append(spot)

	return grid


def draw_grid(win, rows, width):
	"""
	Create grid (Line) of Spot object
	:win (pygame Surface): https://www.pygame.org/docs/ref/surface.html#:~:text=A%20pygame%20Surface%20is%20used,create%20a%20new%20image%20object.
	:rows (int): number of rows and collumn needed
	:width (int): size of screen in pixel

	:return: None
	"""
	gap = width // rows
	for i in range(rows):
		pygame.draw.line(win, GREY, (0, i * gap), (width, i * gap))
		for j in range(rows):
			pygame.draw.line(win, GREY, (j * gap, 0), (j * gap, width))


def draw(win, grid, rows, width):
	"""
	Create color of  each Spot object
	:win (pygame Surface): https://www.pygame.org/docs/ref/surface.html#:~:text=A%20pygame%20Surface%20is%20used,create%20a%20new%20image%20object.
	:grid (List[int][int]: Spot): grid is 2D array of spot
	:rows (int): size of rows in pixel
	:width (int): size of width in pixel

	:return: None
	"""
	win.fill(WHITE)

	for row in grid:
		for spot in row:
			spot.draw(win)

	draw_grid(win, rows, width)
	pygame.display.update()


def get_clicked_pos(pos, rows, width):
	"""
	Calculate which row and col of spot was click
	:pos ((x(int), y(int))): mouse cursor position https://www.pygame.org/docs/ref/mouse.html#pygame.mouse.get_pos
	:rows (int): size of rows in pixel
	:width (int): size of screen in pixel

	:return: row (int), col (int) of spot that was clicked 
	"""
	gap = width // rows	# 1 row or 1 collumn is gap ratio 80/5 = 16
	y, x = pos

	row = y // gap
	col = x // gap

	return row, col


def play_function(win, width, config):
	"""
	Play Controller
	:win (pygame Surface): https://www.pygame.org/docs/ref/surface.html#:~:text=A%20pygame%20Surface%20is%20used,create%20a%20new%20image%20object.
	:width (int): size of screen in pixel
	:config: detail configuration (changing)

	:return: None
	"""
	is_allow_diagonal = config[0][0]
	algorithm = config[4][0]

	ROWS = ROWS_SIZE
	grid = make_grid(ROWS, width)

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
				grid = make_grid(ROWS, width)

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
							if spot.is_closed() or spot.is_open() or spot.is_path():
								spot.reset()
							spot.update_neighbors(grid, is_allow_diagonal)

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
	pygame.display.set_caption("Path Finding Algorithm, (Left,Middle,Right Click, SpaceBar, r)")


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












