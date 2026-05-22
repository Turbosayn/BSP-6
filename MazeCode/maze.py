import pygame
import time
from queue import PriorityQueue

# Updated configuration for better visibility and academic analysis
GRID_SIZE = 600
SIDEBAR_WIDTH = 250
WIDTH = (GRID_SIZE * 2) + SIDEBAR_WIDTH
HEIGHT = 800 
ROWS = 40 
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Academic Pathfinding Analysis: Dijkstra versus A Star")

# Color coded palette for visual representation
WHITE = (255, 255, 255) # Flat Land (Cost 1)
BLACK = (0, 0, 0)       # Wall
GREY = (128, 128, 128)  # Grid Lines
BLUE = (0, 0, 255)      # Water (Cost 2)
BROWN = (139, 69, 19)   # Mountain (Cost 3)
GREEN = (0, 255, 0)     # Start Node
RED = (255, 0, 0)       # Target Node
PURPLE = (128, 0, 128)  # Final Path
TURQUOISE = (64, 224, 208) # Explored Nodes
YELLOW = (255, 255, 0)  # Frontier Nodes
UI_BG = (230, 230, 230) # Sidebar Background
TEXT_COLOR = (30, 30, 30)

pygame.font.init()
FONT = pygame.font.SysFont("Arial", 16)
HEADER_FONT = pygame.font.SysFont("Arial", 18, bold=True)

class Node:
    def __init__(self, row, col, width, total_rows, offset_x=0):
        self.row = row
        self.col = col
        self.x = (row * width) + offset_x
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
    # Manhattan distance calculation for a grid based coordinate system
    x1, y1 = p1
    x2, y2 = p2
    return abs(x1 - x2) + abs(y1 - y2)

def reconstruct_path(came_from, current, draw):
    cost = 0
    length = 0
    while current in came_from:
        cost += current.weight
        length += 1
        current = came_from[current]
        current.make_path()
        if draw: draw()
    return cost, length

def run_algorithm_headless(algo_type, grid, start, end):
    # This function is used by the benchmarking script for fast data collection
    count = 0
    open_set = PriorityQueue()
    open_set.put((0, count, start))
    came_from = {}
    g_score = {node: float("inf") for row in grid for node in row}
    g_score[start] = 0
    nodes_explored = 0
    start_time = time.time()

    while not open_set.empty():
        current = open_set.get()[2]
        nodes_explored += 1
        if current == end:
            cost, length = reconstruct_path(came_from, end, None)
            return {"cost": cost, "explored": nodes_explored, "time": round(time.time() - start_time, 6)}

        for neighbor in current.neighbors:
            temp_g = g_score[current] + neighbor.weight
            if temp_g < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = temp_g
                if algo_type == "A_STAR":
                    f = temp_g + h(neighbor.get_pos(), end.get_pos())
                    open_set.put((f, count, neighbor))
                else: 
                    open_set.put((temp_g, count, neighbor))
                count += 1
    return None

def draw_sidebar(win, brush, results_d, results_a):
    pygame.draw.rect(win, UI_BG, (GRID_SIZE * 2, 0, SIDEBAR_WIDTH, HEIGHT))
    y_pos = 20
    win.blit(HEADER_FONT.render("Controls", True, TEXT_COLOR), (GRID_SIZE * 2 + 20, y_pos))
    y_pos += 30
    controls = ["1: Start | 2: End", "3: Wall | 4: Water", "5: Mountain", "C: Clear Labyrinth", "Z: Undo Clear", "S: Start Side by Side", "R: Reset Visuals"]
    for text in controls:
        win.blit(FONT.render(text, True, TEXT_COLOR), (GRID_SIZE * 2 + 20, y_pos))
        y_pos += 25
    
    y_pos += 20
    win.blit(HEADER_FONT.render(f"Active Brush: {brush}", True, TEXT_COLOR), (GRID_SIZE * 2 + 20, y_pos))
    
    y_pos += 40
    brushes = [("START", GREEN), ("END", RED), ("WALL", BLACK), ("WATER", BLUE), ("MOUNTAIN", BROWN)]
    for name, color in brushes:
        rect_x = GRID_SIZE * 2 + 20
        pygame.draw.rect(win, color, (rect_x, y_pos, 20, 20))
        win.blit(FONT.render(name, True, TEXT_COLOR), (rect_x + 30, y_pos))
        y_pos += 30

    y_pos += 40
    win.blit(HEADER_FONT.render("Dijkstra Results (Left)", True, TEXT_COLOR), (GRID_SIZE * 2 + 20, y_pos))
    if results_d:
        win.blit(FONT.render(f"Path Cost: {results_d['cost']}", True, TEXT_COLOR), (GRID_SIZE * 2 + 20, y_pos + 25))
        win.blit(FONT.render(f"Nodes Explored: {results_d['explored']}", True, TEXT_COLOR), (GRID_SIZE * 2 + 20, y_pos + 45))
        win.blit(FONT.render(f"Time: {results_d['time']}s", True, TEXT_COLOR), (GRID_SIZE * 2 + 20, y_pos + 65))
    
    y_pos += 110
    win.blit(HEADER_FONT.render("A Star Results (Right)", True, TEXT_COLOR), (GRID_SIZE * 2 + 20, y_pos))
    if results_a:
        win.blit(FONT.render(f"Path Cost: {results_a['cost']}", True, TEXT_COLOR), (GRID_SIZE * 2 + 20, y_pos + 25))
        win.blit(FONT.render(f"Nodes Explored: {results_a['explored']}", True, TEXT_COLOR), (GRID_SIZE * 2 + 20, y_pos + 45))
        win.blit(FONT.render(f"Time: {results_a['time']}s", True, TEXT_COLOR), (GRID_SIZE * 2 + 20, y_pos + 65))

def main(win):
    gap = GRID_SIZE // ROWS
    grid_editor = [[Node(i, j, gap, ROWS) for j in range(ROWS)] for i in range(ROWS)]
    grid_d, grid_a = None, None
    grid_backup = None
    start_pos, end_pos = None, None
    brush = "START"
    results_d, results_a = None, None
    sim_state = "EDITING" # EDITING, RUNNING, FINISHED
    run = True

    while run:
        win.fill(WHITE)
        active_grids = [grid_editor] if sim_state == "EDITING" else [grid_d, grid_a]
        for g in active_grids:
            for row in g:
                for node in row: node.draw(win)
        
        for offset in [0, GRID_SIZE] if sim_state != "EDITING" else [0]:
            for i in range(ROWS + 1):
                pygame.draw.line(win, GREY, (offset, i * gap), (offset + GRID_SIZE, i * gap))
                pygame.draw.line(win, GREY, (offset + i * gap, 0), (offset + i * gap, GRID_SIZE))

        draw_sidebar(win, brush, results_d, results_a)
        pygame.display.update()

        if sim_state == "RUNNING":
            count_d, count_a = 0, 0
            open_d, open_a = PriorityQueue(), PriorityQueue()
            open_d.put((0, count_d, grid_d[start_pos[0]][start_pos[1]]))
            open_a.put((0, count_a, grid_a[start_pos[0]][start_pos[1]]))
            
            came_d, came_a = {}, {}
            g_d = {n: float("inf") for r in grid_d for n in r}
            g_a = {n: float("inf") for r in grid_a for n in r}
            g_d[grid_d[start_pos[0]][start_pos[1]]] = 0
            g_a[grid_a[start_pos[0]][start_pos[1]]] = 0
            
            d_done, a_done = False, False
            exp_d, exp_a = 0, 0
            t_sim_start = time.time()

            while not (d_done and a_done):
                if not d_done and not open_d.empty():
                    curr = open_d.get()[2]
                    exp_d += 1
                    if curr.row == end_pos[0] and curr.col == end_pos[1]:
                        cost, length = reconstruct_path(came_d, curr, None)
                        results_d = {"cost": cost, "explored": exp_d, "time": round(time.time() - t_sim_start, 4)}
                        d_done = True
                    else:
                        for n in curr.neighbors:
                            temp = g_d[curr] + n.weight
                            if temp < g_d[n]:
                                came_d[n] = curr
                                g_d[n] = temp
                                count_d += 1
                                open_d.put((temp, count_d, n))
                                n.make_open()
                        if curr.color != GREEN: curr.make_closed()

                if not a_done and not open_a.empty():
                    curr = open_a.get()[2]
                    exp_a += 1
                    if curr.row == end_pos[0] and curr.col == end_pos[1]:
                        cost, length = reconstruct_path(came_a, curr, None)
                        results_a = {"cost": cost, "explored": exp_a, "time": round(time.time() - t_sim_start, 4)}
                        a_done = True
                    else:
                        for n in curr.neighbors:
                            temp = g_a[curr] + n.weight
                            if temp < g_a[n]:
                                came_a[n] = curr
                                g_a[n] = temp
                                count_a += 1
                                f = temp + h(n.get_pos(), end_pos)
                                open_a.put((f, count_a, n))
                                n.make_open()
                        if curr.color != GREEN: curr.make_closed()

                for event in pygame.event.get():
                    if event.type == pygame.QUIT: pygame.quit()
                
                for r in grid_d: 
                    for n in r: n.draw(win)
                for r in grid_a: 
                    for n in r: n.draw(win)
                draw_sidebar(win, brush, results_d, results_a)
                pygame.display.update()

            sim_state = "FINISHED"

        for event in pygame.event.get():
            if event.type == pygame.QUIT: run = False
            if pygame.mouse.get_pressed()[0] and sim_state == "EDITING":
                pos = pygame.mouse.get_pos()
                if pos[0] < GRID_SIZE:
                    r, c = pos[0] // gap, pos[1] // gap
                    node = grid_editor[r][c]
                    if brush == "START":
                        for row in grid_editor:
                            for n in row: 
                                if n.color == GREEN: n.reset()
                        node.make_start()
                        start_pos = (r, c)
                    elif brush == "END":
                        for row in grid_editor:
                            for n in row: 
                                if n.color == RED: n.reset()
                        node.make_end()
                        end_pos = (r, c)
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
                    grid_backup = [[(n.color, n.weight) for n in r] for r in grid_editor]
                    grid_editor = [[Node(i, j, gap, ROWS) for j in range(ROWS)] for i in range(ROWS)]
                    results_d, results_a, sim_state = None, None, "EDITING"
                if event.key == pygame.K_z and grid_backup:
                    for r in range(ROWS):
                        for c in range(ROWS):
                            grid_editor[r][c].color, grid_editor[r][c].weight = grid_backup[r][c]
                            if grid_editor[r][c].color == GREEN: start_pos = (r, c)
                            if grid_editor[r][c].color == RED: end_pos = (r, c)
                if event.key == pygame.K_r: 
                    results_d, results_a, sim_state = None, None, "EDITING"
                if event.key == pygame.K_s and start_pos and end_pos:
                    grid_d = [[Node(i, j, gap, ROWS) for j in range(ROWS)] for i in range(ROWS)]
                    grid_a = [[Node(i, j, gap, ROWS, GRID_SIZE) for j in range(ROWS)] for i in range(ROWS)]
                    for r in range(ROWS):
                        for c in range(ROWS):
                            for target in [grid_d[r][c], grid_a[r][c]]:
                                target.color, target.weight = grid_editor[r][c].color, grid_editor[r][c].weight
                    for g in [grid_d, grid_a]:
                        for r in g:
                            for n in r: n.update_neighbors(g)
                    sim_state = "RUNNING"

    pygame.quit()

if __name__ == "__main__":
    main(WIN)