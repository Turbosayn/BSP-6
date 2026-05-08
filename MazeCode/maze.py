import pygame
import time
import copy
from queue import PriorityQueue

# Configuration for the visual user interface
GRID_WIDTH = 800
SIDEBAR_WIDTH = 250
WIDTH = GRID_WIDTH + SIDEBAR_WIDTH
ROWS = 40 
WIN = pygame.display.set_mode((WIDTH, GRID_WIDTH))
pygame.display.set_caption("Academic Pathfinding Analysis: Dijkstra versus A Star")

# Color coded palette for terrains and UI
WHITE = (255, 255, 255) # Flat Land (Cost 1)
BLACK = (0, 0, 0)       # Wall (Impassable)
GREY = (128, 128, 128)  # Grid Lines
BLUE = (0, 0, 255)      # Water (Cost 2)
BROWN = (139, 69, 19)   # Mountain (Cost 3)
GREEN = (0, 255, 0)     # Start Node
RED = (255, 0, 0)       # Target Node
PURPLE = (128, 0, 128)  # Final Path
TURQUOISE = (64, 224, 208) # Closed Set (Explored)
YELLOW = (255, 255, 0)  # Open Set (Frontier)
UI_BG = (230, 230, 230) # Sidebar Background
TEXT_COLOR = (30, 30, 30)

pygame.font.init()
FONT = pygame.font.SysFont("Arial", 18)
HEADER_FONT = pygame.font.SysFont("Arial", 22, bold=True)

class Node:
    def __init__(self, row, col, width, total_rows):
        self.row = row
        self.col = col
        self.x = row * width
        self.y = col * width
        self.color = WHITE
        self.weight = 1
        self.neighbors = []
        self.width = width
        self.total_rows = total_rows

    def get_pos(self):
        return self.row, self.col

    def reset(self):
        self.color = WHITE
        self.weight = 1

    def make_start(self): self.color = GREEN
    def make_end(self): self.color = RED
    def make_barrier(self): self.color = BLACK
    def make_water(self): 
        self.color = BLUE
        self.weight = 2
    def make_mountain(self): 
        self.color = BROWN
        self.weight = 3
    def make_closed(self): 
        if self.color not in [GREEN, RED, BLUE, BROWN]: self.color = TURQUOISE
    def make_open(self):
        if self.color not in [GREEN, RED, BLUE, BROWN]: self.color = YELLOW
    def make_path(self): self.color = PURPLE

    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))

    def update_neighbors(self, grid):
        self.neighbors = []
        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].color == BLACK:
            self.neighbors.append(grid[self.row + 1][self.col])
        if self.row > 0 and not grid[self.row - 1][self.col].color == BLACK:
            self.neighbors.append(grid[self.row - 1][self.col])
        if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].color == BLACK:
            self.neighbors.append(grid[self.row][self.col + 1])
        if self.col > 0 and not grid[self.row][self.col - 1].color == BLACK:
            self.neighbors.append(grid[self.row][self.col - 1])

def h(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return abs(x1 - x2) + abs(y1 - y2)

def reconstruct_path(came_from, current, draw):
    path_cost = 0
    path_length = 0
    while current in came_from:
        path_cost += current.weight
        path_length += 1
        current = came_from[current]
        current.make_path()
        draw()
    return path_cost, path_length

def run_algorithm(algo_type, draw, grid, start, end):
    count = 0
    open_set = PriorityQueue()
    open_set.put((0, count, start))
    came_from = {}
    g_score = {node: float("inf") for row in grid for node in row}
    g_score[start] = 0
    nodes_explored = 0
    start_time = time.time()

    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit()

        current = open_set.get()[2]
        nodes_explored += 1

        if current == end:
            path_cost, path_length = reconstruct_path(came_from, end, draw)
            end.make_end()
            return {"cost": path_cost, "length": path_length, "explored": nodes_explored, "time": round(time.time() - start_time, 4)}

        for neighbor in current.neighbors:
            temp_g_score = g_score[current] + neighbor.weight
            if temp_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = temp_g_score
                if algo_type == "A_STAR":
                    f_score = temp_g_score + h(neighbor.get_pos(), end.get_pos())
                    open_set.put((f_score, count, neighbor))
                else: 
                    open_set.put((temp_g_score, count, neighbor))
                count += 1
                neighbor.make_open()
        draw()
        if current != start: current.make_closed()
    return None

def draw_grid(win, rows, width):
    gap = width // rows
    for i in range(rows):
        pygame.draw.line(win, GREY, (0, i * gap), (width, i * gap))
        for j in range(rows):
            pygame.draw.line(win, GREY, (j * gap, 0), (j * gap, width))

def draw_sidebar(win, current_brush, last_results):
    pygame.draw.rect(win, UI_BG, (GRID_WIDTH, 0, SIDEBAR_WIDTH, GRID_WIDTH))
    y_offset = 20
    win.blit(HEADER_FONT.render("Tools and Brush", True, TEXT_COLOR), (GRID_WIDTH + 20, y_offset))
    brushes = [("Start (Green)", GREEN), ("End (Red)", RED), ("Wall (Black)", BLACK), 
               ("Water Cost 2 (Blue)", BLUE), ("Mountain Cost 3 (Brown)", BROWN)]
    y_offset += 40
    for name, color in brushes:
        rect = pygame.Rect(GRID_WIDTH + 20, y_offset, 210, 35)
        bg = (200, 200, 200) if current_brush == name.split()[0].upper() else (255, 255, 255)
        pygame.draw.rect(win, bg, rect)
        pygame.draw.rect(win, color, (GRID_WIDTH + 25, y_offset + 7, 20, 20))
        win.blit(FONT.render(name, True, TEXT_COLOR), (GRID_WIDTH + 55, y_offset + 7))
        y_offset += 45
    y_offset += 20
    win.blit(HEADER_FONT.render("Commands", True, TEXT_COLOR), (GRID_WIDTH + 20, y_offset))
    win.blit(FONT.render("SPACE: A Star | D: Dijkstra", True, TEXT_COLOR), (GRID_WIDTH + 20, y_offset + 35))
    win.blit(FONT.render("C: Clear Grid | Z: Undo Clear", True, TEXT_COLOR), (GRID_WIDTH + 20, y_offset + 60))
    y_offset += 110
    win.blit(HEADER_FONT.render("Algorithm Results", True, TEXT_COLOR), (GRID_WIDTH + 20, y_offset))
    if last_results:
        win.blit(FONT.render(f"Path Total Cost: {last_results['cost']}", True, TEXT_COLOR), (GRID_WIDTH + 20, y_offset + 40))
        win.blit(FONT.render(f"Path Node Count: {last_results['length']}", True, TEXT_COLOR), (GRID_WIDTH + 20, y_offset + 65))
        win.blit(FONT.render(f"Nodes Explored: {last_results['explored']}", True, TEXT_COLOR), (GRID_WIDTH + 20, y_offset + 90))
        win.blit(FONT.render(f"Execution Time: {last_results['time']}s", True, TEXT_COLOR), (GRID_WIDTH + 20, y_offset + 115))

def draw_everything(win, grid, rows, width, brush, last_results):
    win.fill(WHITE)
    for row in grid:
        for node in row:
            node.draw(win)
    draw_grid(win, rows, width)
    draw_sidebar(win, brush, last_results)
    pygame.display.update()

def main(win, width):
    gap = GRID_WIDTH // ROWS
    grid = [[Node(i, j, gap, ROWS) for j in range(ROWS)] for i in range(ROWS)]
    grid_backup = None
    start = None
    end = None
    brush = "START"
    last_results = None
    run = True

    while run:
        draw_everything(win, grid, ROWS, GRID_WIDTH, brush, last_results)

        for event in pygame.event.get():
            if event.type == pygame.QUIT: run = False
            if pygame.mouse.get_pressed()[0]:
                pos = pygame.mouse.get_pos()
                if pos[0] < GRID_WIDTH:
                    r, c = pos[0] // gap, pos[1] // gap
                    node = grid[r][c]
                    if brush == "START":
                        if start: start.reset()
                        start = node
                        start.make_start()
                    elif brush == "END":
                        if end: end.reset()
                        end = node
                        end.make_end()
                    elif brush == "WALL": node.make_barrier()
                    elif brush == "WATER": node.make_water()
                    elif brush == "MOUNTAIN": node.make_mountain()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1: brush = "START"
                if event.key == pygame.K_2: brush = "END"
                if event.key == pygame.K_3: brush = "WALL"
                if event.key == pygame.K_4: brush = "WATER"
                if event.key == pygame.K_5: brush = "MOUNTAIN"
                if event.key == pygame.K_c:
                    grid_backup = [[(n.color, n.weight) for n in row] for row in grid]
                    start, end, last_results = None, None, None
                    grid = [[Node(i, j, gap, ROWS) for j in range(ROWS)] for i in range(ROWS)]
                if event.key == pygame.K_z and grid_backup:
                    grid = [[Node(i, j, gap, ROWS) for j in range(ROWS)] for i in range(ROWS)]
                    for r in range(ROWS):
                        for c in range(ROWS):
                            grid[r][c].color, grid[r][c].weight = grid_backup[r][c]
                            if grid[r][c].color == GREEN: start = grid[r][c]
                            if grid[r][c].color == RED: end = grid[r][c]
                    grid_backup = None
                if start and end:
                    if event.key == pygame.K_SPACE:
                        for row in grid:
                            for node in row: node.update_neighbors(grid)
                        last_results = run_algorithm("A_STAR", lambda: draw_everything(win, grid, ROWS, GRID_WIDTH, brush, last_results), grid, start, end)
                    if event.key == pygame.K_d:
                        for row in grid:
                            for node in row: node.update_neighbors(grid)
                        last_results = run_algorithm("DIJKSTRA", lambda: draw_everything(win, grid, ROWS, GRID_WIDTH, brush, last_results), grid, start, end)
    pygame.quit()

main(WIN, WIDTH)