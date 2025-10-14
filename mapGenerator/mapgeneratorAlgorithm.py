import math, heapq, random

PATH, OBSTACLE, PARK, ENTRY = 0, 1, 2, 3

def dijkstra_cost(layout: list[list[int]], start: tuple[int, int], k: float) -> list[list[float]]:
    h, w = len(layout), len(layout[0])
    dist = [[math.inf] * w for _ in range(h)]
    sx, sy = start
    dist[sy][sx] = 0.0
    pq = [(0.0, sx, sy)]
    while pq:
        d, x, y = heapq.heappop(pq)
        if d != dist[y][x]:
            continue
        for dx, dy in [(1,0), (-1,0), (0,1), (0,-1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h:
                cell = layout[ny][nx]
                if cell == OBSTACLE:
                    continue
                step = 1.0 if cell == PATH else k
                nd = d + step
                if nd < dist[ny][nx]:
                    dist[ny][nx] = nd
                    heapq.heappush(pq, (nd, nx, ny))
    return dist

def evaluate_layout(layout: list[list[int]], entries: list[tuple[int, int]], alpha: float, beta: float, k: float) -> tuple[float, float, float]:
    avg_cost = 0
    parks = sum(cell == PARK for row in layout for cell in row)
    for entry in entries:
        dist = dijkstra_cost(layout, entry, k)
        costs = [dist[y][x] for y in range(len(layout)) for x in range(len(layout[0])) if layout[y][x] == PARK and math.isfinite(dist[y][x])]
        if not costs:
            return math.inf, 0, 0
        avg_cost += sum(costs)/parks
    
    density = parks / ((len(layout)-2)*(len(layout[0])-2))
    return (avg_cost * alpha - density * beta * len(entries), avg_cost, density)

def random_layout(mesures, manual_obstacles=None):
    w, h = mesures
    grid = [[PARK for _ in range(w)] for _ in range(h)]

    for x in range(w):
        grid[0][x] = OBSTACLE
        grid[h-1][x] = OBSTACLE
    for y in range(h):
        grid[y][0] = OBSTACLE
        grid[y][w-1] = OBSTACLE

    locked = set()
    if manual_obstacles:
        for ox, oy in manual_obstacles:
            if 0 <= ox < w and 0 <= oy < h:
                grid[oy][ox] = OBSTACLE
                locked.add((ox, oy))

    p = random.choice([3, 4, 5, 6, 7, 8, 9, 10])
    o = random.randint(1, p - 1)
    for x in range(1, w - 1):
        if (x - o) % p == 0:
            for y in range(1, h - 1):
                if (x, y) not in locked:
                    grid[y][x] = PATH

    q = random.choice([3, 4, 5, 6, 7, 8, 9, 10])
    r = random.randint(1, q - 1)
    for y in range(1, h - 1):
        if (y - r) % q == 0:
            for x in range(1, w - 1):
                if (x, y) not in locked:
                    grid[y][x] = PATH

    return grid

def getBestParking(mesures: tuple[int, int], entries: list[tuple[int, int]], obstacles: list[tuple[int, int]], tries: int = 200, alpha: float = 1, beta: float = 3, k: float = 3):
    best = (math.inf, 0, 0, 0)    
    for _ in range(tries):
        manual_obstacles = obstacles.copy()
        for i in range(mesures[1]):
            for j in range(mesures[0]):
                if (i == 0 or i == mesures[1]-1 or j == 0 or j == mesures[0]-1):
                    manual_obstacles.append((j, i))
        rlayout = random_layout(mesures, manual_obstacles)
        score, avg_cost, density = evaluate_layout(rlayout, entries, alpha, beta, k)
        best = (score, avg_cost, density, rlayout) if score < best[0] else best
    return best

def render_ascii(layout, entries):
    chars = {PATH: '·', PARK: 'P', OBSTACLE: '#'}
    return "\n".join(
        "".join('E' if (x,y) in entries else chars[cell] for x,cell in enumerate(row))
        for y,row in enumerate(layout)
    )

if __name__ == "__main__":
    mesures, entries, tries = (6, 6), [(0,3)], 1000
    score, avg_cost, density, layout = getBestParking(mesures, entries, [], tries)
    print((score, avg_cost, density))
    print(render_ascii(layout, entries))