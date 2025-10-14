def createNode(position: tuple[int, int], g: float = float("inf"), h: float = 0.0, parent: dict = None) -> dict:
    return {
        "position": position,
        "g": g,
        "h": h,
        "f": g+h,
        "parent": parent
        }

def heuristic(pos1: tuple[int, int], pos2: tuple[int, int]) -> float:
    return abs(pos2[0]-pos1[0])+abs(pos2[1]-pos1[1])

def reconstructPath(node: dict) -> list:
    path = []
    current = node
    while current["parent"] != None:
        path.append(current["position"])
        current = current["parent"]
    return path[::-1]

def getNeighbours(grid: list[list[int]], node: dict) -> list[tuple[int, int]]:
    neighbours = []
    defaultNeighbours = [(-1,0),(1,0),(0,-1),(0,1)]
    x, y = node["position"]

    for neighbour in defaultNeighbours:
        if grid[y+neighbour[1]][x+neighbour[0]] != 1:
            neighbours.append(neighbour)

    return neighbours

def getCarAddons(grid: list[list[int]], nodePosition: tuple[int, int], k: float = 5.0, j: float = 1.5) -> int:
    x, y = nodePosition
    return k if grid[y][x] == 5 else (j if grid[y][x] == 2 else 0)

def aStar(grid: list[list[int]], start: tuple[int, int], goal: tuple[int, int]) -> list[tuple[int, int]]:
    openList = [createNode(start,0,heuristic(start, goal))]
    closedList = []

    while openList != []:
        current = {"f": float("inf")}
        for node in openList:
            current = node if node["f"] < current["f"] else current

        if current["position"] == goal:
            return reconstructPath(current)
        
        openList.pop(openList.index(current))
        closedList.append(current)

        for neighbor in getNeighbours(grid, current):
            if all(node["position"] != (current["position"][0]+neighbor[0], current["position"][1]+neighbor[1]) for node in closedList):
                tentative_g = current["g"] + heuristic(current["position"], (current["position"][0]+neighbor[0], current["position"][1]+neighbor[1]))+getCarAddons(grid, (current["position"][0]+neighbor[0], current["position"][1]+neighbor[1]))
                if all(node["position"] != (current["position"][0]+neighbor[0], current["position"][1]+neighbor[1]) for node in openList):
                    openList.append(createNode((current["position"][0]+neighbor[0], current["position"][1]+neighbor[1]),tentative_g,heuristic((current["position"][0]+neighbor[0], current["position"][1]+neighbor[1]), goal),current))
                else:
                    neighborNode = None
                    for node in openList:
                        neighborNode = node if node["position"] == (current["position"][0]+neighbor[0], current["position"][1]+neighbor[1]) else neighborNode
                    if tentative_g < neighborNode["g"]:
                        neighborNode["parent"] = current
                        neighborNode["g"] = tentative_g
                        neighborNode["f"] = neighborNode["g"] + neighborNode["h"]
    return False


if __name__ == "__main__":
    mygrid = [[1, 1, 1, 3, 1, 1, 1, 1],
              [1, 2, 2, 0, 2, 2, 2, 1],
              [1, 0, 0, 0, 0, 0, 4, 1],
              [1, 2, 2, 0, 2, 2, 2, 1],
              [1, 1, 1, 1, 1, 1, 1, 1]]
    path = aStar(mygrid,(6, 2),(1, 1))
  
    for position in path:
        mygrid[position[1]][position[0]] = 9

    print(mygrid)