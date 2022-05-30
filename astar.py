import pygame #For visualization
import math
from queue import PriorityQueue
#Width of screen
WIDTH = 800
#Set display window
WIN = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("A* Path Finding Algorithm")

RED = (255, 0, 0)
BLUE = (0, 255, 255)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165 ,0)
GREY = (128, 128, 128)

class Spot:
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
		return self.row, self.col
	
	def is_node(self):
		return self.color == BLUE

	def is_wall(self):
		return self.color == BLACK

	def is_start(self):
		return self.color == ORANGE

	def is_goal(self):
		return self.color == RED

	def reset(self):
		self.color = WHITE

	def make_start(self):
		self.color = ORANGE

	def make_node(self):
		self.color = BLUE

	def make_wall(self):
		self.color = BLACK

	def make_goal(self):
		self.color = RED

	def make_path(self):
		self.color = PURPLE

	def draw(self, win):
		pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))

	#Store neighbors of each cubes
	def update_neighbors(self, grid):
		self.neighbors = []
		if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_wall(): # DOWN
			self.neighbors.append(grid[self.row + 1][self.col])

		if self.row > 0 and not grid[self.row - 1][self.col].is_wall(): # UP
			self.neighbors.append(grid[self.row - 1][self.col])

		if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_wall(): # RIGHT
			self.neighbors.append(grid[self.row][self.col + 1])

		if self.col > 0 and not grid[self.row][self.col - 1].is_wall(): # LEFT
			self.neighbors.append(grid[self.row][self.col - 1])

	def __lt__(self, other):
		return False


def h(p1, p2):
	x1, y1 = p1
	x2, y2 = p2
	return abs(x1 - x2) + abs(y1 - y2)

#make path to goal
def reconstruct_path(came_from, current, draw):
	while current in came_from:
		current = came_from[current]
		current.make_path()
		draw()


def algorithm(draw, grid, start, goal):
	count = 0 #count make sure that if two spots have the same F then we can chose the spot came first
	open_set = PriorityQueue() #data structure for spot
	open_set.put((0, count, start)) #Put first spot into queue
	came_from = {} #keep track of a spot before
	g_score = {spot: float("inf") for row in grid for spot in row} #We assign g_score of every spot is infinity
	g_score[start] = 0 #Of course g_score of start spot == 0
	f_score = {spot: float("inf") for row in grid for spot in row} #Similary, we assign f_score of every spot is infinity
	f_score[start] = h(start.get_pos(), goal.get_pos()) #assign f_score for start spot

	open_set_hash = {start} #With PriorityQueue we can not check whether a spot is in it or not
							#so we make a set that being synchronous with open_set to check it.

	while not open_set.empty(): #If open_set is empty means there is no way reach the goal
		#Next is check for user interaction
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()

		current = open_set.get()[2] #get a spot from the queue, [2] means current is a spot
		open_set_hash.remove(current) #synchronous with the open_set
		#Next is check if the current spot is the goal
		if current == goal:
			reconstruct_path(came_from, goal, draw)
			goal.make_goal() 
			return True
		#If it is not, determine it's nearby spots
		for neighbor in current.neighbors:
			#For every neighbor, we assign temp_g_score
			temp_g_score = g_score[current] + 1 #Why '+1' because is take +1 step from current to it's neighbor

			#Next we check if temp_g_score less than this neighbor in order to 
			# make sure g_score is optimal and no loop between two spots.			
			if temp_g_score < g_score[neighbor]:
				came_from[neighbor] = current #keep track for neighbor
				g_score[neighbor] = temp_g_score #assign this optimal g_score to neighbor
				f_score[neighbor] = g_score[neighbor]+h(neighbor.get_pos(), goal.get_pos()) #get f_score of neighbor
				#If neighbor is in open_set_hash means it's in queue so we don't need to do anything
				#but if it's not
				#add it into queue and open_set_hash
				if neighbor not in open_set_hash:
					count += 1
					open_set.put((f_score[neighbor], count, neighbor))
					open_set_hash.add(neighbor)

		draw()

		if current != start:
			current.make_node()

	return False

#Create a data structure hold all of spots
def make_grid(rows, width):
	grid = [] 
	gap = width // rows #size of each cubes
	for i in range(rows):
		grid.append([])
		for j in range(rows):
			spot = Spot(i, j, gap, rows)
			grid[i].append(spot)

	return grid

#draw lines to create grid
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


def main(win, width):
	ROWS = 50 #number of cubes 50x50
	grid = make_grid(ROWS, width)

	start = None
	goal = None

	run = True
	while run:
		draw(win, grid, ROWS, width)
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False

			if pygame.mouse.get_pressed()[0]: # LEFT MOUSE
				pos = pygame.mouse.get_pos()
				row, col = get_clicked_pos(pos, ROWS, width)
				spot = grid[row][col]

				if not start and spot != goal:
					start = spot
					start.make_start()

				elif not goal and spot != start:
					goal = spot
					goal.make_goal()

				elif spot != goal and spot != start:
					spot.make_wall()

			elif pygame.mouse.get_pressed()[2]: # RIGHT MOUSE
				pos = pygame.mouse.get_pos()
				row, col = get_clicked_pos(pos, ROWS, width)
				spot = grid[row][col]
				spot.reset()
				if spot == start:
					start = None
				elif spot == goal:
					goal = None

			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_SPACE and start and goal:
					for row in grid:
						for spot in row:
							spot.update_neighbors(grid)

					algorithm(lambda: draw(win, grid, ROWS, width), grid, start, goal)

				if event.key == pygame.K_c:
					start = None
					goal = None
					grid = make_grid(ROWS, width)

	pygame.quit()

main(WIN, WIDTH)
