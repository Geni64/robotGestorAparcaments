import os, ast, threading, time, requests
from astar import aStar
from firebase import getDocument, updateDocument, setDocument
import pygame, tkinter.filedialog

# INITIAL INIT FOR CONSTS
pygame.init()
info = pygame.display.Info()

# ──────────────────────────────
# CONSTS
# ──────────────────────────────

# WINDOW CONSTS
WIDTH, HEIGHT = info.current_w, info.current_h
SIZE_REL = WIDTH/1920
WINDOW_NAME = "TDR: SIMULACIÓ"
WINDOW_NAME_X = 7.5*SIZE_REL
WINDOW_NAME_Y = 7.5*SIZE_REL
FONT_SIZE = 20
WINDOW_NAME_COLOR = "black"
BACKGROUND_COLOR = "white"

# TOPBAR CONSTS
TOPBAR_HEIGHT = 35*SIZE_REL
TOPBAR_COLOR = "purple"
CROSS_WIDTH = 30*SIZE_REL
CROSS_HEIGHT = 20*SIZE_REL
CROSS_MARGIN = 10*SIZE_REL
CROSS_LINE_WIDTH = int(5*SIZE_REL)
CROSS_COLOR = "red"

# AVAILABLE WINDOW CONSTS
AVAILABLE_WIDTH, AVAILABLE_HEIGHT = WIDTH, HEIGHT - TOPBAR_HEIGHT
AVAILABLE_X0, AVAILABLE_Y0 = 0, TOPBAR_HEIGHT

# ALERT WINDOW CONSTS
ALERT_WINDOW_WIDTH = 375*SIZE_REL
ALERT_WINDOW_HEIGHT = 150*SIZE_REL
ALERT_WINDOW_BORDER = int(3*SIZE_REL)
ALERT_WINDOW_BUTTON_WIDTH = 100*SIZE_REL
ALERT_WINDOW_BUTTON_HEIGHT = 50*SIZE_REL
ALERT_WINDOW_BUTTON_BORDER = int(3*SIZE_REL)
WINDOW_ALERT_MAIN_TEXT = "Segur que vols tancar l'aplicació?"
WINDOW_ALERT_YES_TEXT = "Sí"
WINDOW_ALERT_NO_TEXT = "No"
WINDOW_ALERT_BACKGROUND_COLOR = "white"
WINDOW_ALERT_MAIN_COLOR = "black"
WINDOW_ALERT_YES_COLOR = "green"
WINDOW_ALERT_NO_COLOR = "red"
ALERT_WINDOW_X = WIDTH//2-ALERT_WINDOW_WIDTH//2
ALERT_WINDOW_Y = HEIGHT//2-ALERT_WINDOW_HEIGHT//2

# CHOOSE FILE CONSTS
CHOOSE_FILE_BUTTON_WIDTH = 200*SIZE_REL
CHOOSE_FILE_BUTTON_HEIGHT = 80*SIZE_REL
CHOOSE_FILE_BUTTON_MARGIN_X = 50*SIZE_REL
CHOOSE_FILE_BUTTON_MARGIN_Y = 65*SIZE_REL
CHOOSE_FILE_BUTTON_COLOR = "brown"
CHOOSE_FILE_TEXT_COLOR = "black"
CHOOSE_FILE_MAIN_TEXT = "Obre un fitxer"

# GRID CONSTS
ROBOT_SIZE = (169, 240)
CAR_SIZE = (225, 290)

# GRID INFO CONSTS
INFOFONT_SIZE = 15*SIZE_REL
ELEMENT_INFO_TEXT_MARGIN_X = 30*SIZE_REL
ELEMENT_INFO_TEXT_MARGIN_Y = 30*SIZE_REL
ELEMENT_INFO_TEXTS_MARGIN_Y = 15*SIZE_REL
ELEMENT_INFO_TEXT_COLOR = "black"
ELEMENT_INFO_TEXT1 = "%s position: (%s, %s)"
ELEMENT_INFO_TEXT2 = "%s objective: %s"
ELEMENT_INFO_OPT1 = "%s transporting: %s"

# PARKING CONSTS
SERVER_IP = "127.0.0.1:5000"
MILLISPERCELLX = 250
MILLISPERCELLY = 500
ASTAR_DELAY = 500
PATH, OBSTACLE, PARK, ENTRY, ROBOT, CAR = 0, 1, 2, 3, 4, 5
PARKING_COLORS = {
    0: "white",
    1: "black",
    2: "yellow2",
    3: "springgreen1",
    4: "purple",
    5: "orange",
    100: "red",
    102: (246, 246, 127),
    103: (127, 255, 191),
    104: (207, 143, 247),
    200: (255, 127, 127),
    300: "darkgreen"
}
ROBOT_MOVEMENTS = {
    "stoprobot" : {
    "m1a": 0, "m1b": 0,
    "m2a": 0, "m2b": 0,
    "m3a": 0, "m3b": 0,
    "m4a": 0, "m4b": 0
    },
    "forward" : {
    "m1a": 1, "m1b": 0,
    "m2a": 0, "m2b": 1,
    "m3a": 0, "m3b": 1,
    "m4a": 1, "m4b": 0
    },
    "backward" : {
    "m1a": 0, "m1b": 1,
    "m2a": 1, "m2b": 0,
    "m3a": 1, "m3b": 0,
    "m4a": 0, "m4b": 1
    },
    "right" : {
    "m1a": 0, "m1b": 1,
    "m2a": 0, "m2b": 1,
    "m3a": 0, "m3b": 1,
    "m4a": 0, "m4b": 1
    },
    "left" : {
    "m1a": 1, "m1b": 0,
    "m2a": 1, "m2b": 0,
    "m3a": 1, "m3b": 0,
    "m4a": 1, "m4b": 0
    },
    "up" : {
    "s1":  180, "s2":  180
    },
    "down" : {
    "s1":  0, "s2":  0
    }
}

# ──────────────────────────────
# INIT
# ──────────────────────────────


pygame.font.init()
font = pygame.font.Font(os.path.realpath("simulation/assets/super_lobster.ttf"), int(FONT_SIZE*SIZE_REL))
infoFont = pygame.font.Font(os.path.realpath("simulation/assets/Roboto-Thin.ttf"), int(INFOFONT_SIZE*SIZE_REL))
info = pygame.display.Info()
appScreen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption(WINDOW_NAME)
running = True

# ──────────────────────────────
# FUNCTIONS
# ──────────────────────────────

def gridMousePosition(mouse_pos: tuple[int, int]) -> tuple[int, int]:
    return None if marginX > mouse_pos[0] or mouse_pos[0] > marginX+screenCarSize[0]*gridCols or marginY > mouse_pos[1] or mouse_pos[1] > marginY+screenCarSize[1]*gridRows or int((mouse_pos[0]-marginX)//screenCarSize[0]) < 0 or int((mouse_pos[0]-marginX)//screenCarSize[0]) > gridCols-1 or int((mouse_pos[1]-marginY)//screenCarSize[1]) < 0 or int((mouse_pos[1]-marginY)//screenCarSize[1]) > gridRows-1 else (int((mouse_pos[0]-marginX)//screenCarSize[0]), int((mouse_pos[1]-marginY)//screenCarSize[1]))

def runPark():
    global gridMap, tempGridMap, aStarParkGoal, robotPos, startCarPos, aStarParkPath, aStarParkWorking, aStarParkFinished, aStarParkPathActions
    aStarParkWorking, aStarParkFinished = True, False
    aStarParkPath, aStarParkPathActions = [], []
    gridMap[parkSpot[1]][parkSpot[0]] = CAR

    aStarParkPath += aStar(gridMap, robotPos, startCarPos)
    aStarParkPathActions.append([len(aStarParkPath)-1, "up"])
    aStarParkPath += aStar(gridMap, startCarPos, aStarParkGoal)
    aStarParkPathActions.append([len(aStarParkPath)-1, "down"])
    aStarParkPath += aStar(gridMap, aStarParkGoal, idleRobotPos)
    aStarParkWorking, aStarParkFinished = False, True

def runUnpark():
    global gridMap, tempGridMap, aStarUnparkGoal, robotPos, startCarPos, aStarUnparkPath, aStarUnparkWorking, aStarUnparkFinished, parkingData, aStarUnparkPathActions
    aStarUnparkWorking, aStarUnparkFinished = True, False
    aStarUnparkPath, aStarUnparkPathActions = [], []
    parks = {}
    aStarPath = aStar(gridMap, robotPos, aStarUnparkGoal)

    tempGridMap = [[0] * gridCols for _ in range(gridRows)]
    carsInvolved = []
    closestCars = []
    closestPathStopG = None
    for cell in aStarPath:
        if gridMap[cell[1]][cell[0]] == CAR and cell != aStarUnparkGoal:
            carsInvolved.append(cell)

    for car in carsInvolved[::-1]:
        closestCar = None
        closestPathStop = closestPathStopG
        possibleCars = []
        bestCar = float("inf")
        for i, row in enumerate(gridMap):
            for j, cell in enumerate(row):
                if gridMap[i][j] == PATH and (j, i) not in aStarPath and (j, i) != car:
                    possibleCars.append((j, i))
        for possibleCar in possibleCars:
            possiblePathStop = None
            trip = aStar(gridMap, possibleCar, car)
            tripLenght = len(trip)
            tripCollision = None
            for i, cell in enumerate(aStarPath):
                if gridMap[cell[1]][cell[0]] == PARK and tripCollision == None:
                    for j in range(i-3):
                        if aStarPath[j] in trip:
                            tripCollision = True
            tripCollision = False if tripCollision == None else tripCollision
            if tripLenght < bestCar and all(possibleCar != c for c in closestCars) and not tripCollision:
                closestCar = possibleCar
                bestCar = tripLenght
                if closestPathStopG == None:
                    for i, cell in enumerate(aStarPath):
                        if cell in trip and possiblePathStop == None:
                            possiblePathStop = aStarPath[i-1]
                    closestPathStop = possiblePathStop
        closestCars.append(closestCar)
        closestPathStopG = closestPathStop
    
    for car in closestCars:
        tempGridMap[car[1]][car[0]] = 100
    if closestPathStopG != None:
        tempGridMap[closestPathStopG[1]][closestPathStopG[0]] = 300

    robotTempPos = robotPos
    if closestPathStopG != None:
        for i in range(len(carsInvolved)):
            aStarUnparkPath += aStar(gridMap, robotTempPos, carsInvolved[i])
            aStarUnparkPathActions.append([len(aStarUnparkPath)-1, "up"])
            aStarUnparkPath += aStar(gridMap, carsInvolved[i], closestCars[i])
            aStarUnparkPathActions.append([len(aStarUnparkPath)-1, "down"])
            parks[str(carsInvolved[i])] = 0
            gridMap[carsInvolved[i][1]][carsInvolved[i][0]] = PARK
            robotTempPos = closestCars[i]
        aStarUnparkPath += aStar(gridMap, robotTempPos, aStarUnparkGoal)
        aStarUnparkPathActions.append([len(aStarUnparkPath)-1, "up"])
        aStarUnparkPath += aStar(gridMap, aStarUnparkGoal, closestPathStopG)
        aStarUnparkPathActions.append([len(aStarUnparkPath)-1, "down"])
        gridMap[aStarUnparkGoal[1]][aStarUnparkGoal[0]] = PARK
        robotTempPos = closestPathStopG
        tempCarsInvolved = carsInvolved.copy()
        tempCarsInvolved.pop(0)
        tempCarsInvolved.append(aStarUnparkGoal)
        for i in range(len(tempCarsInvolved)-1, -1, -1):
            aStarUnparkPath += aStar(gridMap, robotTempPos, closestCars[i])
            aStarUnparkPathActions.append([len(aStarUnparkPath)-1, "up"])
            aStarUnparkPath += aStar(gridMap, closestCars[i], tempCarsInvolved[i])
            aStarUnparkPathActions.append([len(aStarUnparkPath)-1, "down"])
            parks[str(tempCarsInvolved[i])] = parkingData[str(carsInvolved[i])]
            gridMap[tempCarsInvolved[i][1]][tempCarsInvolved[i][0]] = CAR
            robotTempPos = tempCarsInvolved[i]
        aStarUnparkPath += aStar(gridMap, robotTempPos, closestPathStopG)
        aStarUnparkPathActions.append([len(aStarUnparkPath)-1, "up"])
        aStarUnparkPath += aStar(gridMap, closestPathStopG, startCarPos)
        aStarUnparkPathActions.append([len(aStarUnparkPath)-1, "down"])
    else:
        aStarUnparkPath += aStar(gridMap, robotTempPos, aStarUnparkGoal)
        aStarUnparkPathActions.append([len(aStarUnparkPath)-1, "up"])
        aStarUnparkPath += aStar(gridMap, aStarUnparkGoal, startCarPos)
        aStarUnparkPathActions.append([len(aStarUnparkPath)-1, "down"])
        gridMap[aStarUnparkGoal[1]][aStarUnparkGoal[0]] = PARK
        parks[str(aStarUnparkGoal)] = 0
    aStarUnparkPath += aStar(gridMap, startCarPos, idleRobotPos)

    updateDocument(parkingName, parks)
    
    aStarUnparkWorking, aStarUnparkFinished = False, True

# ──────────────────────────────
# VARIABLES
# ──────────────────────────────

# FILE CHOOSING
file_chosen = False
file_chosen_firstTime = True
file_path = ""

# GRID MAP
gridMap = None
tempGridMap = None
gridCols = 0
gridRows = 0
gridMousePos = None
screenCarSize = None
marginX = 0
marginY = 0

# A* ALGORITHM
aStarParkGoal = None
aStarParkPath = None
aStarParkPathActions = None
aStarUnparkGoal = None
aStarUnparkPath = None
aStarUnparkPathActions = None
fullPath = None
parkSpots = []
aStarParkWorking, aStarParkFinished = False, False
aStarUnparkWorking, aStarUnparkFinished = False, False
trackLastCellTime = 0
currentTrackIndex = 0
currentTrack = None
currentTrackActions = None

# SIMULATION START
robotPos = None
startCarPos = None
idleRobotPos = None
parkingData = None
car_pos = []
carOnRobot = False
lastAStarUse = 0
actuators_values = {
    "m1a": 0, "m1b": 0,
    "m2a": 0, "m2b": 0,
    "m3a": 0, "m3b": 0,
    "m4a": 0, "m4b": 0,
    "s1":  0, "s2":  0
}
millispercelltowait = 0

# ALERT WINDOW
alert_window = False

# ──────────────────────────────
# APP LOOP
# ──────────────────────────────

while running and pygame.font:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    appScreen.fill(BACKGROUND_COLOR)

    # ──────────────────────────────
    # GATHER INFO
    # ──────────────────────────────

    keys = pygame.key.get_pressed()
    left, middle, right = pygame.mouse.get_pressed()
    mouse_pos = pygame.mouse.get_pos()
    if keys[pygame.K_ESCAPE]:
        alert_window = True

    # ──────────────────────────────
    # MAIN WINDOW DRAWING
    # ──────────────────────────────
    if file_chosen and file_path != "":
        
        # ──────────────────────────────
        # GRID DRAWING
        # ──────────────────────────────
        
        if file_chosen_firstTime:
            carRatio = min((AVAILABLE_WIDTH-30)/gridCols/CAR_SIZE[0], (AVAILABLE_HEIGHT-30)/gridRows/CAR_SIZE[1])
            screenCarSize = (CAR_SIZE[0]*carRatio, CAR_SIZE[1]*carRatio)
            marginX = (AVAILABLE_WIDTH-screenCarSize[0]*gridCols)//2
            marginY = (AVAILABLE_HEIGHT-screenCarSize[1]*gridRows)//2+TOPBAR_HEIGHT
            file_chosen_firstTime = False

        for i, row in enumerate(gridMap):
            for j, col in enumerate(row):
                pygame.draw.polygon(appScreen, PARKING_COLORS[ROBOT] if (j, i) == robotPos else PARKING_COLORS[col], ((marginX+screenCarSize[0]*j, marginY+screenCarSize[1]*i),(marginX+screenCarSize[0]*(1+j), marginY+screenCarSize[1]*i),(marginX+screenCarSize[0]*(1+j), marginY+screenCarSize[1]*(1+i)),(marginX+screenCarSize[0]*j, marginY+screenCarSize[1]*(1+i))))

        if not all(col == 0 for col in (row for row in tempGridMap)):
            for i, row in enumerate(tempGridMap):
                for j, col in enumerate(row):
                    if col != 0:
                        pygame.draw.polygon(appScreen, PARKING_COLORS[col], ((marginX+screenCarSize[0]*j, marginY+screenCarSize[1]*i),(marginX+screenCarSize[0]*(1+j), marginY+screenCarSize[1]*i),(marginX+screenCarSize[0]*(1+j), marginY+screenCarSize[1]*(1+i)),(marginX+screenCarSize[0]*j, marginY+screenCarSize[1]*(1+i))))

        pygame.draw.polygon(appScreen, PARKING_COLORS[ROBOT], ((marginX+screenCarSize[0]*robotPos[0], marginY+screenCarSize[1]*robotPos[1]),(marginX+screenCarSize[0]*(1+robotPos[0]), marginY+screenCarSize[1]*robotPos[1]),(marginX+screenCarSize[0]*(1+robotPos[0]), marginY+screenCarSize[1]*(1+robotPos[1])),(marginX+screenCarSize[0]*robotPos[0], marginY+screenCarSize[1]*(1+robotPos[1]))))

        for i in range(gridRows+1):
            pygame.draw.line(appScreen, PARKING_COLORS[100], (marginX, marginY+screenCarSize[1]*i), (marginX+screenCarSize[0]*gridCols, marginY+screenCarSize[1]*i), 5)
        for i in range(gridCols+1):
            pygame.draw.line(appScreen, PARKING_COLORS[100], (marginX+screenCarSize[0]*i, marginY), (marginX+screenCarSize[0]*i, marginY+screenCarSize[1]*gridRows), 5)

        # ──────────────────────────────
        # INFO TEXT DRAWING
        # ──────────────────────────────

        gridMousePos = gridMousePosition(mouse_pos)

        if gridMousePos != None:
            if robotPos == gridMousePos:
                elementInfoText1 = infoFont.render(ELEMENT_INFO_TEXT1 % ("ROBOT", robotPos[0], robotPos[1]), True, ELEMENT_INFO_TEXT_COLOR)
                elementInfoText1Position = elementInfoText1.get_rect(x=AVAILABLE_X0+ELEMENT_INFO_TEXT_MARGIN_X, y=AVAILABLE_Y0+ELEMENT_INFO_TEXT_MARGIN_Y)
                elementInfoText2 = infoFont.render(ELEMENT_INFO_OPT1 % ("ROBOT", carOnRobot), True, ELEMENT_INFO_TEXT_COLOR)
                elementInfoText2Position = elementInfoText2.get_rect(x=AVAILABLE_X0+ELEMENT_INFO_TEXT_MARGIN_X, y=AVAILABLE_Y0+ELEMENT_INFO_TEXT_MARGIN_Y*2)
                appScreen.blit(elementInfoText1, elementInfoText1Position)
                appScreen.blit(elementInfoText2, elementInfoText2Position)
            elif startCarPos == gridMousePos:
                elementInfoText1 = infoFont.render(ELEMENT_INFO_TEXT1 % ("SCAR", startCarPos[0], startCarPos[1]), True, ELEMENT_INFO_TEXT_COLOR)
                elementInfoText1Position = elementInfoText1.get_rect(x=AVAILABLE_X0+ELEMENT_INFO_TEXT_MARGIN_X, y=AVAILABLE_Y0+ELEMENT_INFO_TEXT_MARGIN_Y)
                appScreen.blit(elementInfoText1, elementInfoText1Position)
            else:
                for car in car_pos:
                    if car == gridMousePos:
                        elementInfoText1 = infoFont.render(ELEMENT_INFO_TEXT1 % ("CAR", car[0], car[1]), True, ELEMENT_INFO_TEXT_COLOR)
                        elementInfoText1Position = elementInfoText1.get_rect(x=AVAILABLE_X0+ELEMENT_INFO_TEXT_MARGIN_X, y=AVAILABLE_Y0+ELEMENT_INFO_TEXT_MARGIN_Y)
                        appScreen.blit(elementInfoText1, elementInfoText1Position)

        # ──────────────────────────────
        # ASTAR
        # ──────────────────────────────
        if pygame.time.get_ticks()-lastAStarUse >= ASTAR_DELAY or aStarParkWorking:
            parkingData = getDocument(parkingName)

            if not aStarParkWorking and not aStarParkFinished and not aStarUnparkWorking and not aStarUnparkFinished:
                if parkingData["start"] != ["ç", "ç"] and currentTrack == None:
                    parkSpot = None

                    for park in parkSpots:
                        if parkingData[str(park)] == 0 and parkSpot == None:
                            parkSpot = park
                    
                    if parkSpot != None:
                        aStarParkGoal = parkSpot
                        threading.Thread(target=runPark).start()
                    else:
                        print("NO SPACE LEFT :(")
                elif parkingData["end"] != ["ç", "ç"] and currentTrack == None:
                    aStarUnparkGoal = ast.literal_eval(parkingData["end"][-1])
                    threading.Thread(target=runUnpark).start()

            elif aStarParkFinished:
                print(aStarParkPath)
                start = parkingData["start"][:-1]
                updateDocument(parkingName, {str(aStarParkGoal) : parkingData["start"][-1],
                                            "start" : start})
                aStarParkWorking = False
                aStarParkFinished = False
                
                currentTrack = aStarParkPath
                currentTrackActions = aStarParkPathActions
                trackStartTime = pygame.time.get_ticks()

            elif aStarUnparkFinished:
                print(aStarUnparkPath)
                end = parkingData["end"][:-1]
                updateDocument(parkingName, {"end" : end})
                aStarUnparkWorking = False
                aStarUnparkFinished = False

                currentTrack = aStarUnparkPath
                currentTrackActions = aStarUnparkPathActions
                trackStartTime = pygame.time.get_ticks()

            lastAStarUse = pygame.time.get_ticks()
        
        if currentTrack != None and pygame.time.get_ticks()-trackLastCellTime >= millispercelltowait:
            robotPos = currentTrack[currentTrackIndex]
            print(time.time(),robotPos, actuators_values)
            requests.post(f"http://{SERVER_IP}/set-orders", json=actuators_values)
            if currentTrackIndex + 1 == len(currentTrack):
                trackLastCellTime = 0
                currentTrackIndex = 0
                currentTrack = None
                currentTrackActions = None
                desiredMovement = "stoprobot"
                desiredServo = "down"
                millispercelltowait = 0
                
                actuators_values["s1"] = ROBOT_MOVEMENTS[desiredServo]["s1"]
                actuators_values["s2"] = ROBOT_MOVEMENTS[desiredServo]["s2"]
                actuators_values["m1a"] = ROBOT_MOVEMENTS[desiredMovement]["m1a"]
                actuators_values["m1b"] = ROBOT_MOVEMENTS[desiredMovement]["m1b"]
                actuators_values["m2a"] = ROBOT_MOVEMENTS[desiredMovement]["m2a"]
                actuators_values["m2b"] = ROBOT_MOVEMENTS[desiredMovement]["m2b"]
                actuators_values["m3a"] = ROBOT_MOVEMENTS[desiredMovement]["m3a"]
                actuators_values["m3b"] = ROBOT_MOVEMENTS[desiredMovement]["m3b"]
                actuators_values["m4a"] = ROBOT_MOVEMENTS[desiredMovement]["m4a"]
                actuators_values["m4b"] = ROBOT_MOVEMENTS[desiredMovement]["m4b"]

                requests.post(f"http://{SERVER_IP}/set-orders", json=actuators_values)

            else:
                currentTrackIndex += 1
                deltaMovementX = robotPos[0]-currentTrack[currentTrackIndex][0]
                deltaMovementY = robotPos[1]-currentTrack[currentTrackIndex][1]
                desiredMovement = "stoprobot"
                desiredServo = "stopservo"

                for i in currentTrackActions:
                    if i[0] == currentTrackIndex-1:
                        desiredServo = i[1]
                        currentTrackActions.remove(i)
                        break
                
                if desiredServo == "stopservo":
                    if deltaMovementX == 1:
                        desiredMovement = "left"
                        millispercelltowait = MILLISPERCELLX
                    elif deltaMovementX == -1:
                        desiredMovement = "right"
                        millispercelltowait = MILLISPERCELLX
                    elif deltaMovementY == 1:
                        desiredMovement = "forward"
                        millispercelltowait = MILLISPERCELLY
                    elif deltaMovementY == -1:
                        desiredMovement = "backward"
                        millispercelltowait = MILLISPERCELLY
                else:
                    actuators_values["s1"] = ROBOT_MOVEMENTS[desiredServo]["s1"]
                    actuators_values["s2"] = ROBOT_MOVEMENTS[desiredServo]["s2"]
                    currentTrackIndex -= 1

                actuators_values["m1a"] = ROBOT_MOVEMENTS[desiredMovement]["m1a"]
                actuators_values["m1b"] = ROBOT_MOVEMENTS[desiredMovement]["m1b"]
                actuators_values["m2a"] = ROBOT_MOVEMENTS[desiredMovement]["m2a"]
                actuators_values["m2b"] = ROBOT_MOVEMENTS[desiredMovement]["m2b"]
                actuators_values["m3a"] = ROBOT_MOVEMENTS[desiredMovement]["m3a"]
                actuators_values["m3b"] = ROBOT_MOVEMENTS[desiredMovement]["m3b"]
                actuators_values["m4a"] = ROBOT_MOVEMENTS[desiredMovement]["m4a"]
                actuators_values["m4b"] = ROBOT_MOVEMENTS[desiredMovement]["m4b"]
                
                trackLastCellTime = pygame.time.get_ticks()

    else:
        pygame.draw.rect(appScreen, CHOOSE_FILE_BUTTON_COLOR, (AVAILABLE_X0+CHOOSE_FILE_BUTTON_MARGIN_X, AVAILABLE_Y0+CHOOSE_FILE_BUTTON_MARGIN_Y, CHOOSE_FILE_BUTTON_WIDTH, CHOOSE_FILE_BUTTON_HEIGHT))

        chooseFileText = font.render(CHOOSE_FILE_MAIN_TEXT, True, CHOOSE_FILE_TEXT_COLOR)
        chooseFileTextPosition = chooseFileText.get_rect(x=AVAILABLE_X0+CHOOSE_FILE_BUTTON_MARGIN_X+30, y=AVAILABLE_Y0+CHOOSE_FILE_BUTTON_MARGIN_Y+30)
        appScreen.blit(chooseFileText, chooseFileTextPosition)

        if left and AVAILABLE_X0+CHOOSE_FILE_BUTTON_MARGIN_X<mouse_pos[0]<AVAILABLE_X0+CHOOSE_FILE_BUTTON_MARGIN_X+CHOOSE_FILE_BUTTON_WIDTH and AVAILABLE_Y0+CHOOSE_FILE_BUTTON_MARGIN_Y<mouse_pos[1]<AVAILABLE_Y0+CHOOSE_FILE_BUTTON_MARGIN_Y+CHOOSE_FILE_BUTTON_HEIGHT:
            file_path = tkinter.filedialog.askopenfilename(title=CHOOSE_FILE_MAIN_TEXT, filetypes=[("TDR files", "*.tdr")])
            if file_path == "":
                continue
            file_chosen = True

            tmpFile = open(file_path, "r")
            tmpData = tmpFile.read().split("ñ")
            tmpFile.close()

            parkingName = os.path.basename(file_path)
            robotPos = ast.literal_eval(tmpData[0])
            startCarPos = ast.literal_eval(tmpData[1])
            car_pos = ast.literal_eval(tmpData[2])
            gridMap = ast.literal_eval(tmpData[3])
            gridRows = len(gridMap)
            gridCols = len(gridMap[0])  
            tempGridMap = [[0] * gridCols for _ in range(gridRows)]

            if startCarPos[0] == 0:
                idleRobotPos = (1, startCarPos[1])
            elif startCarPos[0] == gridCols-1:
                idleRobotPos = (gridCols-2, startCarPos[1])
            elif startCarPos[1] == 0:
                idleRobotPos = (startCarPos[0], 1)
            else:
                idleRobotPos = (startCarPos[0], gridRows-2)

            parks = {"start" : ["ç", "ç"],
                     "end" : ["ç", "ç"],
                     "robotPos" : robotPos}
            parkingData = getDocument(parkingName)

            for i, row in enumerate(gridMap):
                    for j, col in enumerate(row):
                        if col == PARK:
                            parks[str((j, i))] = 0
                            parkSpots.append((j, i))

            if "ERROR" not in parkingData:
                for park in parkSpots:
                    if parkingData[f"({park[0]}, {park[1]})"] != 0:
                            gridMap[park[1]][park[0]] = CAR
                robotPos = parkingData["robotPos"]
            else:
                setDocument(parkingName, parks)
                time.sleep(1)


    # ──────────────────────────────
    # TOPBAR DRAWING
    # ──────────────────────────────

    pygame.draw.rect(appScreen, TOPBAR_COLOR, (0, 0, WIDTH, TOPBAR_HEIGHT))
    # TEXT APP
    windowNameText = font.render(WINDOW_NAME, True, WINDOW_NAME_COLOR)
    windowNameTextPosition = windowNameText.get_rect(x=WINDOW_NAME_X, y=WINDOW_NAME_Y)
    appScreen.blit(windowNameText, windowNameTextPosition)
    # ICONA TANCAR
    pygame.draw.line(appScreen, CROSS_COLOR, (WIDTH-CROSS_WIDTH-CROSS_MARGIN, (TOPBAR_HEIGHT-CROSS_HEIGHT)//2), (WIDTH-CROSS_MARGIN, (TOPBAR_HEIGHT-CROSS_HEIGHT)//2+CROSS_HEIGHT), CROSS_LINE_WIDTH)
    pygame.draw.line(appScreen, CROSS_COLOR, (WIDTH-CROSS_MARGIN, (TOPBAR_HEIGHT-CROSS_HEIGHT)//2), (WIDTH-CROSS_WIDTH-CROSS_MARGIN, (TOPBAR_HEIGHT-CROSS_HEIGHT)//2+CROSS_HEIGHT), CROSS_LINE_WIDTH)
    # FUNCIONAMENT TANCAR
    if left and WIDTH-CROSS_WIDTH-CROSS_MARGIN<mouse_pos[0]<WIDTH-CROSS_MARGIN and (TOPBAR_HEIGHT-CROSS_HEIGHT)//2<mouse_pos[1]<(TOPBAR_HEIGHT-CROSS_HEIGHT)//2+CROSS_HEIGHT:
        alert_window = True
            
    if alert_window:
        pygame.draw.rect(appScreen, WINDOW_ALERT_BACKGROUND_COLOR, (ALERT_WINDOW_X, ALERT_WINDOW_Y, ALERT_WINDOW_WIDTH, ALERT_WINDOW_HEIGHT))
        pygame.draw.rect(appScreen, WINDOW_ALERT_MAIN_COLOR, (ALERT_WINDOW_X, ALERT_WINDOW_Y, ALERT_WINDOW_WIDTH, ALERT_WINDOW_HEIGHT), ALERT_WINDOW_BORDER)
        pygame.draw.rect(appScreen, WINDOW_ALERT_YES_COLOR, (ALERT_WINDOW_X+10, ALERT_WINDOW_Y+ALERT_WINDOW_HEIGHT-ALERT_WINDOW_BUTTON_HEIGHT-10, ALERT_WINDOW_BUTTON_WIDTH, ALERT_WINDOW_BUTTON_HEIGHT), ALERT_WINDOW_BUTTON_BORDER)
        pygame.draw.rect(appScreen, WINDOW_ALERT_NO_COLOR, (ALERT_WINDOW_X+ALERT_WINDOW_WIDTH-ALERT_WINDOW_BUTTON_WIDTH-10, ALERT_WINDOW_Y+ALERT_WINDOW_HEIGHT-ALERT_WINDOW_BUTTON_HEIGHT-10, ALERT_WINDOW_BUTTON_WIDTH, ALERT_WINDOW_BUTTON_HEIGHT), ALERT_WINDOW_BUTTON_BORDER)

        alertWindowMainText = font.render(WINDOW_ALERT_MAIN_TEXT, True, WINDOW_ALERT_MAIN_COLOR)
        alertWindowMainTextPosition = alertWindowMainText.get_rect(x=ALERT_WINDOW_X+15, y=ALERT_WINDOW_Y+15)

        alertWindowYesText = font.render(WINDOW_ALERT_YES_TEXT, True, WINDOW_ALERT_YES_COLOR)
        alertWindowYesTextPosition = alertWindowYesText.get_rect(x=ALERT_WINDOW_X+(ALERT_WINDOW_BUTTON_WIDTH/2), y=ALERT_WINDOW_Y+ALERT_WINDOW_HEIGHT-(ALERT_WINDOW_BUTTON_HEIGHT/2)-20)

        alertWindowNoText = font.render(WINDOW_ALERT_NO_TEXT, True, WINDOW_ALERT_NO_COLOR)
        alertWindowNoTextPosition = alertWindowYesText.get_rect(x=ALERT_WINDOW_X+ALERT_WINDOW_WIDTH-(ALERT_WINDOW_BUTTON_WIDTH/2)-20, y=ALERT_WINDOW_Y+ALERT_WINDOW_HEIGHT-(ALERT_WINDOW_BUTTON_HEIGHT/2)-20)

        appScreen.blit(alertWindowMainText, alertWindowMainTextPosition)
        appScreen.blit(alertWindowYesText, alertWindowYesTextPosition)
        appScreen.blit(alertWindowNoText, alertWindowNoTextPosition)

        if left and ALERT_WINDOW_X+10<mouse_pos[0]<ALERT_WINDOW_X+10+ALERT_WINDOW_BUTTON_WIDTH and ALERT_WINDOW_Y+ALERT_WINDOW_HEIGHT-ALERT_WINDOW_BUTTON_HEIGHT-10<mouse_pos[1]<ALERT_WINDOW_Y+ALERT_WINDOW_HEIGHT-10:
            running = False
        elif left and ALERT_WINDOW_X+ALERT_WINDOW_WIDTH-ALERT_WINDOW_BUTTON_WIDTH-10<mouse_pos[0]<ALERT_WINDOW_X+ALERT_WINDOW_WIDTH-10 and ALERT_WINDOW_Y+ALERT_WINDOW_HEIGHT-ALERT_WINDOW_BUTTON_HEIGHT-10<mouse_pos[1]<ALERT_WINDOW_Y+ALERT_WINDOW_HEIGHT-10:
            alert_window = False

    # ──────────────────────────────
    # WINDOW UPDATING
    # ──────────────────────────────

    pygame.display.flip()


pygame.quit()