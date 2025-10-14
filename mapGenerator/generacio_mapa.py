import ezdxf, copy, os, uuid, threading
import pygame, tkinter.filedialog
from mapgeneratorAlgorithm import getBestParking, render_ascii

# INITIAL INIT FOR CONSTS
pygame.init()
info = pygame.display.Info()

# ──────────────────────────────
# CONSTS
# ──────────────────────────────

# WINDOW CONSTS
WIDTH, HEIGHT = info.current_w, info.current_h
SIZE_REL = WIDTH/1920
WINDOW_NAME = "TDR: GENERACIÓ DEL MAPA PEL ROBOT"
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

# TOOLS CONSTS
TOOLS_WIDTH = 375*SIZE_REL
TOOLS_HEIGHT = 100*SIZE_REL
TOOL_WIDTH = 70*SIZE_REL
TOOL_HEIGHT = 70*SIZE_REL
TOOLS_MARGIN_X = 50*SIZE_REL
TOOLS_MARGIN_Y = 50*SIZE_REL
TOOLS_BORDER = int(3*SIZE_REL)
TOOLS_BACKGROUND_COLOR = "white"
TOOLS_MAIN_COLOR = "black"
NUMBER_TOOLS = 3
TOOLS_1_MAIN_COLOR = (255, 201, 201)
TOOLS_2_MAIN_COLOR = (178, 242, 187)
TOOLS_3_MAIN_COLOR = (255, 236, 153)
TOOLS_1_SEC_COLOR = "red"
TOOLS_2_SEC_COLOR = "green"
TOOLS_3_SEC_COLOR = "yellow"
TOOLS_2_OPT_COLOR = "black"
CHANGE_TOOL_DELAY = 150

# TOOLS DELAY CONSTS
TOOL_1_DELAY = 250
TOOL_2_DELAY = 250
TOOL_3_DELAY = 250


# CHOOSE FILE CONSTS
CHOOSE_FILE_BUTTON_WIDTH = 200*SIZE_REL
CHOOSE_FILE_BUTTON_HEIGHT = 80*SIZE_REL
CHOOSE_FILE_BUTTON_MARGIN_X = 50*SIZE_REL
CHOOSE_FILE_BUTTON_MARGIN_Y = 65*SIZE_REL
CHOOSE_FILE_BUTTON_COLOR = "brown"
CHOOSE_FILE_TEXT_COLOR = "black"
CHOOSE_FILE_MAIN_TEXT = "Obre un fitxer"

# GRID CONSTS
GRID_SIZE = 10 # mm --> 0.01 cm --> 0.0001 m
ROBOT_SIZE = (169, 240)
CAR_SIZE = (225, 290)

# MAP ALGORITHM CONSTS
THREAD_DELAY = 1000
PATH, OBSTACLE, PARK, ENTRY, ROBOT = 0, 1, 2, 3, 4
TPARK, TENTRY, TROBOT = 102, 103, 104
PARKING_COLORS = {
    0: "white",
    1: "black",
    2: "yellow2",
    3: "springgreen1",
    4: "purple",
    100: "red",
    102: (246, 246, 127),
    103: (127, 255, 191),
    104: (207, 143, 247)
}

# ──────────────────────────────
# INIT
# ──────────────────────────────

pygame.font.init()
font = pygame.font.Font(os.path.realpath("mapGenerator/assets/super_lobster.ttf"), int(FONT_SIZE*SIZE_REL))
info = pygame.display.Info()
appScreen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption(WINDOW_NAME)
running = True

# ──────────────────────────────
# VARIABLES
# ──────────────────────────────

# FILE CHOOSING
file_chosen = False
file_chosen_firstTime = True
file_path = ""

# DXF FILE
originalMap = None
mspOriginalMap = None

# DRAW INFO
drawHeight = 0
drawWidth = 0
screenCarSize = None

# TOOLS
chosen_tool = 0
change_tool_last_use = 0
tool_1_last_use = 0
tool_2_last_use = 0
tool_3_last_use = 0
robotPos = None
startCarPos = None
car_pos = []

# GRID MAP
gridMap = None
tempGridMap = None
originalGridMap = None

# ALERT WINDOW
alert_window = False
alert_window_x = WIDTH//2-ALERT_WINDOW_WIDTH//2
alert_window_y = HEIGHT//2-ALERT_WINDOW_HEIGHT//2

# MAP ALGORITHM
thread_last_use = 0
parkingGeneratorExecuted = False
parkingGeneratorFinished = False
parkingEntry = None
parkingScore = None
parkingAvg_cost = None
parkingDensity = None
parkingLayout = None
manualObstacles = []

# ──────────────────────────────
# FUNCTIONS
# ──────────────────────────────

def run_get_best_parking():
    global parkingScore, parkingAvg_cost, parkingDensity, parkingLayout, gridCols, gridRows, startCarPos, parkingGeneratorExecuted, manualObstacles, parkingGeneratorFinished
    if startCarPos != None:
        parkingScore, parkingAvg_cost, parkingDensity, parkingLayout = getBestParking((gridCols, gridRows),[startCarPos],manualObstacles, 10000)
        print(parkingScore, parkingAvg_cost, parkingDensity)
        print(render_ascii(parkingLayout, [startCarPos]))
        if parkingGeneratorFinished:
            parkingLayout = None
            parkingGeneratorFinished = False
    else:
        parkingGeneratorExecuted = False

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
    elif keys[pygame.K_y] and pygame.time.get_ticks()-thread_last_use >= THREAD_DELAY and not parkingGeneratorExecuted:
        threading.Thread(target=run_get_best_parking).start()
        thread_last_use = pygame.time.get_ticks()
        parkingGeneratorExecuted = True

    # ──────────────────────────────
    # MAIN WINDOW DRAWING
    # ──────────────────────────────
    if file_chosen and file_path != "":
        
        # ──────────────────────────────
        # PARKING ALGORITHM
        # ──────────────────────────────     

        if parkingGeneratorExecuted and not parkingGeneratorFinished:
            if parkingLayout != None:
                parkingGeneratorFinished = (parkingScore != None)
                gridMap = copy.deepcopy(originalGridMap)
                gridMap[startCarPos[1]][startCarPos[0]] = ENTRY
                for h, row in enumerate(parkingLayout):
                    for g, col in enumerate(row):
                        if col == PARK and h!=0 and g!=0 and h!=len(parkingLayout)-1 and g!=len(parkingLayout[0])-1:
                            gridMap[h][g] = col
                            car_pos.append((g, h))
                tempGridMap = [[0] * gridCols for _ in range(gridRows)]
                parkingGeneratorExecuted = False

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

        for i in range(gridRows+1):
            pygame.draw.line(appScreen, PARKING_COLORS[100], (marginX, marginY+screenCarSize[1]*i), (marginX+screenCarSize[0]*gridCols, marginY+screenCarSize[1]*i), 5)
        for i in range(gridCols+1):
            pygame.draw.line(appScreen, PARKING_COLORS[100], (marginX+screenCarSize[0]*i, marginY), (marginX+screenCarSize[0]*i, marginY+screenCarSize[1]*gridRows), 5)
  
        # ──────────────────────────────
        # TOOLS DRAWING
        # ──────────────────────────────
        
        # MAIN TOOLS
        pygame.draw.rect(appScreen, TOOLS_BACKGROUND_COLOR, (TOOLS_MARGIN_X, HEIGHT-TOOLS_MARGIN_Y-TOOLS_HEIGHT, TOOLS_WIDTH, TOOLS_HEIGHT))
        pygame.draw.rect(appScreen, TOOLS_MAIN_COLOR, (TOOLS_MARGIN_X, HEIGHT-TOOLS_MARGIN_Y-TOOLS_HEIGHT, TOOLS_WIDTH, TOOLS_HEIGHT), TOOLS_BORDER)

        # TOOL 1
        pygame.draw.rect(appScreen, TOOLS_1_MAIN_COLOR, (TOOLS_MARGIN_X+(TOOLS_WIDTH-TOOL_WIDTH*NUMBER_TOOLS)//(NUMBER_TOOLS+1), HEIGHT-TOOLS_MARGIN_Y-TOOLS_HEIGHT+(TOOLS_HEIGHT-TOOL_HEIGHT)//2, TOOL_WIDTH, TOOL_HEIGHT))
        pygame.draw.rect(appScreen, TOOLS_1_SEC_COLOR, (TOOLS_MARGIN_X+(TOOLS_WIDTH-TOOL_WIDTH*NUMBER_TOOLS)//(NUMBER_TOOLS+1), HEIGHT-TOOLS_MARGIN_Y-TOOLS_HEIGHT+(TOOLS_HEIGHT-TOOL_HEIGHT)//2, TOOL_WIDTH, TOOL_HEIGHT), TOOLS_BORDER)

        # TOOL 2
        pygame.draw.rect(appScreen, TOOLS_2_MAIN_COLOR, (TOOLS_MARGIN_X+((TOOLS_WIDTH-TOOL_WIDTH*NUMBER_TOOLS)//(NUMBER_TOOLS+1))*2+TOOL_WIDTH*1, HEIGHT-TOOLS_MARGIN_Y-TOOLS_HEIGHT+(TOOLS_HEIGHT-TOOL_HEIGHT)//2, TOOL_WIDTH, TOOL_HEIGHT))
        pygame.draw.rect(appScreen, TOOLS_2_SEC_COLOR, (TOOLS_MARGIN_X+((TOOLS_WIDTH-TOOL_WIDTH*NUMBER_TOOLS)//(NUMBER_TOOLS+1))*2+TOOL_WIDTH*1, HEIGHT-TOOLS_MARGIN_Y-TOOLS_HEIGHT+(TOOLS_HEIGHT-TOOL_HEIGHT)//2, TOOL_WIDTH, TOOL_HEIGHT), TOOLS_BORDER)

        # TOOL 3
        pygame.draw.rect(appScreen, TOOLS_3_MAIN_COLOR, (TOOLS_MARGIN_X+((TOOLS_WIDTH-TOOL_WIDTH*NUMBER_TOOLS)//(NUMBER_TOOLS+1))*3+TOOL_WIDTH*2, HEIGHT-TOOLS_MARGIN_Y-TOOLS_HEIGHT+(TOOLS_HEIGHT-TOOL_HEIGHT)//2, TOOL_WIDTH, TOOL_HEIGHT))
        pygame.draw.rect(appScreen, TOOLS_3_SEC_COLOR, (TOOLS_MARGIN_X+((TOOLS_WIDTH-TOOL_WIDTH*NUMBER_TOOLS)//(NUMBER_TOOLS+1))*3+TOOL_WIDTH*2, HEIGHT-TOOLS_MARGIN_Y-TOOLS_HEIGHT+(TOOLS_HEIGHT-TOOL_HEIGHT)//2, TOOL_WIDTH, TOOL_HEIGHT), TOOLS_BORDER)

        # FUNCIONAMENT ESCOLLIR TOOLS
        if left and TOOLS_MARGIN_X+(TOOLS_WIDTH-TOOL_WIDTH*NUMBER_TOOLS)//(NUMBER_TOOLS+1)<mouse_pos[0]<TOOLS_MARGIN_X+(TOOLS_WIDTH-TOOL_WIDTH*NUMBER_TOOLS)//(NUMBER_TOOLS+1)+TOOL_WIDTH and HEIGHT-TOOLS_MARGIN_Y-TOOLS_HEIGHT+(TOOLS_HEIGHT-TOOL_HEIGHT)//2<mouse_pos[1]<HEIGHT-TOOLS_MARGIN_Y-TOOLS_HEIGHT+(TOOLS_HEIGHT-TOOL_HEIGHT)//2+TOOL_HEIGHT and pygame.time.get_ticks()-change_tool_last_use >= CHANGE_TOOL_DELAY:
            chosen_tool = 1
            change_tool_last_use = pygame.time.get_ticks()
            tool_1_last_use = pygame.time.get_ticks()
        elif left and TOOLS_MARGIN_X+((TOOLS_WIDTH-TOOL_WIDTH*NUMBER_TOOLS)//(NUMBER_TOOLS+1))*2+TOOL_WIDTH*1<mouse_pos[0]<TOOLS_MARGIN_X+((TOOLS_WIDTH-TOOL_WIDTH*NUMBER_TOOLS)//(NUMBER_TOOLS+1))*2+TOOL_WIDTH*2 and HEIGHT-TOOLS_MARGIN_Y-TOOLS_HEIGHT+(TOOLS_HEIGHT-TOOL_HEIGHT)//2<mouse_pos[1]<HEIGHT-TOOLS_MARGIN_Y-TOOLS_HEIGHT+(TOOLS_HEIGHT-TOOL_HEIGHT)//2+TOOL_HEIGHT and pygame.time.get_ticks()-change_tool_last_use >= CHANGE_TOOL_DELAY:
            chosen_tool = 2
            change_tool_last_use = pygame.time.get_ticks()
            tool_2_last_use = pygame.time.get_ticks()
        elif left and TOOLS_MARGIN_X+((TOOLS_WIDTH-TOOL_WIDTH*NUMBER_TOOLS)//(NUMBER_TOOLS+1))*3+TOOL_WIDTH*2<mouse_pos[0]<TOOLS_MARGIN_X+((TOOLS_WIDTH-TOOL_WIDTH*NUMBER_TOOLS)//(NUMBER_TOOLS+1))*3+TOOL_WIDTH*3 and HEIGHT-TOOLS_MARGIN_Y-TOOLS_HEIGHT+(TOOLS_HEIGHT-TOOL_HEIGHT)//2<mouse_pos[1]<HEIGHT-TOOLS_MARGIN_Y-TOOLS_HEIGHT+(TOOLS_HEIGHT-TOOL_HEIGHT)//2+TOOL_HEIGHT and pygame.time.get_ticks()-change_tool_last_use >= CHANGE_TOOL_DELAY:       
            chosen_tool = 3
            change_tool_last_use = pygame.time.get_ticks()
            tool_3_last_use = pygame.time.get_ticks()
        
        # ──────────────────────────────
        # TOOLS WORKING
        # ──────────────────────────────
        
        gridMousePosition = None if marginX > mouse_pos[0] or mouse_pos[0] > marginX+screenCarSize[0]*gridCols or marginY > mouse_pos[1] or mouse_pos[1] > marginY+screenCarSize[1]*gridRows or int((mouse_pos[0]-marginX)//screenCarSize[0]) < 0 or int((mouse_pos[0]-marginX)//screenCarSize[0]) > gridCols-1 or int((mouse_pos[1]-marginY)//screenCarSize[1]) < 0 or int((mouse_pos[1]-marginY)//screenCarSize[1]) > gridRows-1 else (int((mouse_pos[0]-marginX)//screenCarSize[0]), int((mouse_pos[1]-marginY)//screenCarSize[1]))
        
        if chosen_tool == 1 and gridMousePosition != None and pygame.time.get_ticks()-tool_1_last_use >= TOOL_1_DELAY and not alert_window:
            if gridMap[gridMousePosition[1]][gridMousePosition[0]] == PATH:
                tempGridMap = [[0] * gridCols for _ in range(gridRows)]
                if gridMap[gridMousePosition[1]][gridMousePosition[0]] == PATH and robotPos == None and left:
                    robotPos = gridMousePosition
                    tool_1_last_use = pygame.time.get_ticks()
                elif gridMousePosition == robotPos and right:
                    robotPos = None
                    tool_1_last_use = pygame.time.get_ticks()
                elif robotPos == None:
                    tempGridMap[gridMousePosition[1]][gridMousePosition[0]] = TROBOT

        elif chosen_tool == 2 and gridMousePosition != None and pygame.time.get_ticks()-tool_2_last_use >= TOOL_2_DELAY and not alert_window:
            if gridMap[gridMousePosition[1]][gridMousePosition[0]] in (OBSTACLE, ENTRY) and gridMousePosition not in ((0,0), (0,gridRows-1), (gridCols-1, 0), (gridCols-1, gridRows-1)):
                tempGridMap = [[0] * gridCols for _ in range(gridRows)]
                if gridMap[gridMousePosition[1]][gridMousePosition[0]] == OBSTACLE and startCarPos == None and left:
                    gridMap[gridMousePosition[1]][gridMousePosition[0]] = ENTRY
                    startCarPos = gridMousePosition
                    tool_2_last_use = pygame.time.get_ticks()
                elif gridMap[gridMousePosition[1]][gridMousePosition[0]] == ENTRY and right:
                    gridMap[gridMousePosition[1]][gridMousePosition[0]] = OBSTACLE
                    startCarPos = None
                    tool_2_last_use = pygame.time.get_ticks()
                elif startCarPos == None:
                    tempGridMap[gridMousePosition[1]][gridMousePosition[0]] = TENTRY

        elif chosen_tool == 3 and gridMousePosition != None and pygame.time.get_ticks()-tool_3_last_use >= TOOL_3_DELAY and not alert_window:
            if gridMap[gridMousePosition[1]][gridMousePosition[0]] in (PATH, PARK):
                tempGridMap = [[0] * gridCols for _ in range(gridRows)]
                if gridMap[gridMousePosition[1]][gridMousePosition[0]] == PATH and left:
                    gridMap[gridMousePosition[1]][gridMousePosition[0]] = PARK
                    car_pos.append(gridMousePosition)
                    tool_3_last_use = pygame.time.get_ticks()
                elif gridMap[gridMousePosition[1]][gridMousePosition[0]] == PARK and right:
                    gridMap[gridMousePosition[1]][gridMousePosition[0]] = PATH
                    car_pos.pop(car_pos.index(gridMousePosition))
                    tool_3_last_use = pygame.time.get_ticks()
                else:
                    tempGridMap[gridMousePosition[1]][gridMousePosition[0]] = TPARK

    else:
        pygame.draw.rect(appScreen, CHOOSE_FILE_BUTTON_COLOR, (AVAILABLE_X0+CHOOSE_FILE_BUTTON_MARGIN_X, AVAILABLE_Y0+CHOOSE_FILE_BUTTON_MARGIN_Y, CHOOSE_FILE_BUTTON_WIDTH, CHOOSE_FILE_BUTTON_HEIGHT))

        chooseFileText = font.render(CHOOSE_FILE_MAIN_TEXT, True, CHOOSE_FILE_TEXT_COLOR)
        chooseFileTextPosition = chooseFileText.get_rect(x=AVAILABLE_X0+CHOOSE_FILE_BUTTON_MARGIN_X+30, y=AVAILABLE_Y0+CHOOSE_FILE_BUTTON_MARGIN_Y+30)
        appScreen.blit(chooseFileText, chooseFileTextPosition)

        if left and AVAILABLE_X0+CHOOSE_FILE_BUTTON_MARGIN_X<mouse_pos[0]<AVAILABLE_X0+CHOOSE_FILE_BUTTON_MARGIN_X+CHOOSE_FILE_BUTTON_WIDTH and AVAILABLE_Y0+CHOOSE_FILE_BUTTON_MARGIN_Y<mouse_pos[1]<AVAILABLE_Y0+CHOOSE_FILE_BUTTON_MARGIN_Y+CHOOSE_FILE_BUTTON_HEIGHT:
            file_path = tkinter.filedialog.askopenfilename(title=CHOOSE_FILE_MAIN_TEXT, filetypes=[("Drawing Exchange Format", ".dxf")])
            if file_path == "":
                continue
            file_chosen = True

            # DEFINE THE DXF FILE & GET WIDTH, HEIGHT
            originalMap = ezdxf.readfile(file_path)
            mspOriginalMap = originalMap.modelspace()

            for line in mspOriginalMap.query("LINE"):
                start = (line.dxf.start.x, line.dxf.start.y)
                end = (line.dxf.end.x, line.dxf.end.y)

                if start[0] > drawWidth:
                    drawWidth = start[0]
                if end[0] > drawWidth:
                    drawWidth = end[0]
                if start[1] > drawHeight:
                    drawHeight = start[1]
                if end[1] > drawHeight:
                    drawHeight = end[1]

            # CREATING THE GRID
            gridCols = int(drawWidth//CAR_SIZE[0])+2
            gridRows = int(drawHeight//CAR_SIZE[1])+2
            gridMap = [[PATH] * gridCols for _ in range(gridRows)]
            tempGridMap = [[PATH] * gridCols for _ in range(gridRows)]


            # CREATING OBJ IN GRID
            for element in mspOriginalMap:
                if element.dxftype() == "LINE":
                    start = (element.dxf.start.x, element.dxf.start.y)
                    end = (element.dxf.end.x, element.dxf.end.y)
                    if start[0] != 0 and start[0] != drawWidth and end[0] != 0 and end[0] != drawWidth:
                        if start[0] == end[0]: # in case alpha = 90º
                            rmin = min(start[1], end[1])
                            for i in range(int(abs(start[1]-end[1]))):
                                tempGridMap[1+int((rmin+i)//CAR_SIZE[1])][1+int(start[0]//CAR_SIZE[0])] = OBSTACLE
                                manualObstacles.append((1+int(start[0]//CAR_SIZE[0]), 1+int((rmin+i)//CAR_SIZE[1])))
                        elif start[1] == end[1]: # in case alpha = 0º
                            rmin = min(start[0], end[0])
                            for i in range(int(abs(start[0]-end[0]))):
                                tempGridMap[1+int(start[1]//CAR_SIZE[1])][1+int((rmin+1)//CAR_SIZE[0])] = OBSTACLE
                                manualObstacles.append((1+int((rmin+1)//CAR_SIZE[0]), 1+int(start[1]//CAR_SIZE[1])))
            
            for i, row in enumerate(tempGridMap):
                gridMap[gridRows-i-1] = row
            
            for i in range(gridRows):
                for j in range(gridCols):
                    if i == 0 or j == 0 or i == gridRows-1 or j == gridCols-1:
                        gridMap[i][j] = OBSTACLE
            originalGridMap = copy.deepcopy(gridMap)

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
        pygame.draw.rect(appScreen, WINDOW_ALERT_BACKGROUND_COLOR, (alert_window_x, alert_window_y, ALERT_WINDOW_WIDTH, ALERT_WINDOW_HEIGHT))
        pygame.draw.rect(appScreen, WINDOW_ALERT_MAIN_COLOR, (alert_window_x, alert_window_y, ALERT_WINDOW_WIDTH, ALERT_WINDOW_HEIGHT), ALERT_WINDOW_BORDER)
        pygame.draw.rect(appScreen, WINDOW_ALERT_YES_COLOR, (alert_window_x+10, alert_window_y+ALERT_WINDOW_HEIGHT-ALERT_WINDOW_BUTTON_HEIGHT-10, ALERT_WINDOW_BUTTON_WIDTH, ALERT_WINDOW_BUTTON_HEIGHT), ALERT_WINDOW_BUTTON_BORDER)
        pygame.draw.rect(appScreen, WINDOW_ALERT_NO_COLOR, (alert_window_x+ALERT_WINDOW_WIDTH-ALERT_WINDOW_BUTTON_WIDTH-10, alert_window_y+ALERT_WINDOW_HEIGHT-ALERT_WINDOW_BUTTON_HEIGHT-10, ALERT_WINDOW_BUTTON_WIDTH, ALERT_WINDOW_BUTTON_HEIGHT), ALERT_WINDOW_BUTTON_BORDER)

        alertWindowMainText = font.render(WINDOW_ALERT_MAIN_TEXT, True, WINDOW_ALERT_MAIN_COLOR)
        alertWindowMainTextPosition = alertWindowMainText.get_rect(x=alert_window_x+15, y=alert_window_y+15)

        alertWindowYesText = font.render(WINDOW_ALERT_YES_TEXT, True, WINDOW_ALERT_YES_COLOR)
        alertWindowYesTextPosition = alertWindowYesText.get_rect(x=alert_window_x+(ALERT_WINDOW_BUTTON_WIDTH/2), y=alert_window_y+ALERT_WINDOW_HEIGHT-(ALERT_WINDOW_BUTTON_HEIGHT/2)-20)

        alertWindowNoText = font.render(WINDOW_ALERT_NO_TEXT, True, WINDOW_ALERT_NO_COLOR)
        alertWindowNoTextPosition = alertWindowYesText.get_rect(x=alert_window_x+ALERT_WINDOW_WIDTH-(ALERT_WINDOW_BUTTON_WIDTH/2)-20, y=alert_window_y+ALERT_WINDOW_HEIGHT-(ALERT_WINDOW_BUTTON_HEIGHT/2)-20)

        appScreen.blit(alertWindowMainText, alertWindowMainTextPosition)
        appScreen.blit(alertWindowYesText, alertWindowYesTextPosition)
        appScreen.blit(alertWindowNoText, alertWindowNoTextPosition)

        if left and alert_window_x+10<mouse_pos[0]<alert_window_x+10+ALERT_WINDOW_BUTTON_WIDTH and alert_window_y+ALERT_WINDOW_HEIGHT-ALERT_WINDOW_BUTTON_HEIGHT-10<mouse_pos[1]<alert_window_y+ALERT_WINDOW_HEIGHT-10:
            running = False
        elif left and alert_window_x+ALERT_WINDOW_WIDTH-ALERT_WINDOW_BUTTON_WIDTH-10<mouse_pos[0]<alert_window_x+ALERT_WINDOW_WIDTH-10 and alert_window_y+ALERT_WINDOW_HEIGHT-ALERT_WINDOW_BUTTON_HEIGHT-10<mouse_pos[1]<alert_window_y+ALERT_WINDOW_HEIGHT-10:
            alert_window = False
            tool_1_last_use = pygame.time.get_ticks()
            tool_2_last_use = pygame.time.get_ticks()
            tool_3_last_use = pygame.time.get_ticks()
        
    # ──────────────────────────────
    # WINDOW UPDATING
    # ──────────────────────────────

    pygame.display.flip()

# ──────────────────────────────
# QUITTING AND SAVING
# ──────────────────────────────

pygame.quit()

if file_chosen:
    saveOption = input("Would you like to save your work (Y/N)?")

    if file_chosen and saveOption == "Y":
        random_name = uuid.uuid4()
        export_filepath = os.path.dirname(file_path)+"/"+f"{random_name}.tdr"
        exportFile = open(export_filepath, "w")
        exportFile.write(f"{robotPos}ñ{startCarPos}ñ{car_pos}ñ{gridMap}")
        exportFile.close()
        print(f"Saved on: {export_filepath}")