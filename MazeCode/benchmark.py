import time
import csv
import random
from queue import PriorityQueue

# Import the core logic from your main file
# Ensure your main file is named 'pathfinding_main.py' or update this import
# from pathfinding_main import Node, h, dijkstra_algorithm, a_star_algorithm

# For this example, we redefine the core logic briefly to ensure it runs headless
def get_h(p1, p2):
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

def run_benchmarks():
    # Define the parameters for the scientific experiment
    grid_sizes = [20, 40, 60, 80, 100]
    obstacle_density = 0.20 # Twenty percent of the grid is walls
    trials_per_size = 10
    
    results = []
    print("Beginning automated batch processing...")

    for size in grid_sizes:
        print(f"Testing grid size: {size} by {size}")
        for trial in range(trials_per_size):
            # 1. Generate a random environment
            nodes = [[(i, j) for j in range(size)] for i in range(size)]
            barriers = set()
            for i in range(size):
                for j in range(size):
                    if random.random() < obstacle_density:
                        barriers.add((i, j))
            
            start = (0, 0)
            end = (size - 1, size - 1)
            
            # Ensure start and end are not in walls
            if start in barriers: barriers.remove(start)
            if end in barriers: barriers.remove(end)

            # 2. Run Dijkstra Headless
            d_explored, d_time, d_cost = execute_headless("DIJKSTRA", size, start, end, barriers)
            
            # 3. Run A Star Headless
            a_explored, a_time, a_cost = execute_headless("ASTAR", size, start, end, barriers)

            # Store the data point
            results.append({
                "GridSize": size,
                "Trial": trial + 1,
                "D_Explored": d_explored,
                "D_Time": d_time,
                "D_Cost": d_cost,
                "A_Explored": a_explored,
                "A_Time": a_time,
                "A_Cost": a_cost
            })

    # 4. Save to Comma Separated Values file
    with open('pathfinding_results.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)
    
    print("Benchmarking complete. Data saved to pathfinding_results.csv")

def execute_headless(algo, size, start, end, barriers):
    count = 0
    open_set = PriorityQueue()
    open_set.put((0, count, start))
    g_score = { (i, j): float("inf") for i in range(size) for j in range(size) }
    g_score[start] = 0
    explored_count = 0
    start_time = time.time()

    while not open_set.empty():
        current = open_set.get()[2]
        explored_count += 1

        if current == end:
            execution_time = time.time() - start_time
            return explored_count, round(execution_time, 6), g_score[end]

        # Get neighbors
        r, c = current
        neighbors = []
        if r < size - 1: neighbors.append((r + 1, c))
        if r > 0: neighbors.append((r - 1, c))
        if c < size - 1: neighbors.append((r, c + 1))
        if c > 0: neighbors.append((r, c - 1))

        for neighbor in neighbors:
            if neighbor in barriers: continue
            
            temp_g = g_score[current] + 1
            if temp_g < g_score[neighbor]:
                g_score[neighbor] = temp_g
                count += 1
                if algo == "ASTAR":
                    f_score = temp_g + get_h(neighbor, end)
                    open_set.put((f_score, count, neighbor))
                else:
                    open_set.put((temp_g, count, neighbor))
                    
    return explored_count, round(time.time() - start_time, 6), float("inf")

if __name__ == "__main__":
    run_benchmarks()