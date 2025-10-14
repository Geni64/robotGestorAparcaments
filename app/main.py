import os, pygame, math
import tkinter, tkinter.ttk
from firebase import getCollection, getDocument, updateDocument

# INITIAL INIT FOR CONSTS
pygame.init()
info = pygame.display.Info()

# ──────────────────────────────
# CONSTS
# ──────────────────────────────

# WINDOW CONSTS
WIDTH, HEIGHT = 430, 780
SIZE_REL = WIDTH/430
WINDOW_NAME = "TDR: APP"
WINDOW_NAME_X = 7.5*SIZE_REL
WINDOW_NAME_Y = 7.5*SIZE_REL
FONT_SIZE = 20
WINDOW_NAME_COLOR = "black"
BACKGROUND_COLOR = "white"

# BOTTOM BAR CONSTS
BOTTOMBAR_HEIGHT = 60*SIZE_REL
BOTTOMBAR_COLOR = "gray"
BOTTOMBAR_OPTIONS = 3
BOTTOMBAR_OPTIONS_RADIUS = 10
BOTTOMBAR_OPTIONS_SELECTED_COLOR = "black"
BOTTOMBAR_OPTIONS_BASE_COLOR = "azure4"

# AVAILABLE WINDOW CONSTS
AVAILABLE_WIDTH, AVAILABLE_HEIGHT = WIDTH, HEIGHT - BOTTOMBAR_HEIGHT
AVAILABLE_X0, AVAILABLE_Y0 = 0, BOTTOMBAR_HEIGHT

# MANAGE CARS CONSTS
MANAGECARS_MARGINY = 30
MANAGECARS_MARGINX = 10
MANAGECARS_HEIGHT = 100
MANAGECARS_BASE_COLOR = "gray"
MANAGECARS_TEXT_COLOR = "azure4"

# ──────────────────────────────
# INIT
# ──────────────────────────────

pygame.font.init()
font = pygame.font.Font(os.path.realpath("app/assets/Roboto-Thin.ttf"), int(FONT_SIZE*SIZE_REL))
appScreen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption(WINDOW_NAME)
running = True

# ──────────────────────────────
# FUNCTIONS
# ──────────────────────────────

def dropdownSelector(options):
    def accept_selection():
        global dropdownSelectorChoice
        dropdownSelectorChoice = combo.get()
        root.destroy()

    root = tkinter.Tk()
    root.title("Dropdown Selector")
    root.geometry("300x80")

    combo = tkinter.ttk.Combobox(root, values=options, state="readonly", width=250)
    combo.current(0)
    combo.pack(padx=20, pady=10)

    accept_button = tkinter.Button(root, text="Accept", command=accept_selection)
    accept_button.pack(pady=10)

    root.mainloop()

# ──────────────────────────────
# VARIABLES
# ──────────────────────────────

# SCREEN SELECTION
selectedScreen = 0

# USER_OPTIONS
username = "patata"
userCars = getDocument(username, "users")["userCars"]

# DROPDOWN SELECTOR
dropdownSelectorChoice = None

# ──────────────────────────────
# APP LOOP
# ──────────────────────────────

while running and pygame.font:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    appScreen.fill(BACKGROUND_COLOR)
    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

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
    
    if selectedScreen == 0:
        debugText = font.render("DEBUG: DASHBOARD", True, "black")
        debugTextPosition = debugText.get_rect(x=0, y=0)
        appScreen.blit(debugText, debugTextPosition)
    elif selectedScreen == 1:
        for i, car in enumerate(userCars):
            carNameText, carNameTextPosition = None, None
            sectionStart = (MANAGECARS_MARGINX, MANAGECARS_MARGINY+(MANAGECARS_MARGINY+MANAGECARS_HEIGHT)*i)
            pygame.draw.polygon(appScreen, MANAGECARS_BASE_COLOR, (sectionStart, (WIDTH-MANAGECARS_MARGINX, MANAGECARS_MARGINY+(MANAGECARS_MARGINY+MANAGECARS_HEIGHT)*i), (WIDTH-MANAGECARS_MARGINX, (MANAGECARS_MARGINY+MANAGECARS_HEIGHT)*(1+i)), (MANAGECARS_MARGINX, (MANAGECARS_MARGINY+MANAGECARS_HEIGHT)*(1+i))))
            carNameText = font.render(f"{car["name"]} - {car["plate"]}", True, "black")
            carNameTextPosition = carNameText.get_rect(x=sectionStart[0]+5, y=sectionStart[1]+5)
            appScreen.blit(carNameText, carNameTextPosition)
            pygame.draw.polygon(appScreen, car["color"], ((carNameTextPosition.topright[0]+10, carNameTextPosition.topright[1]), (carNameTextPosition.topright[0]+40, carNameTextPosition.topright[1]), (carNameTextPosition.topright[0]+40, carNameTextPosition.topright[1]+20), (carNameTextPosition.topright[0]+10, carNameTextPosition.topright[1]+20)))
            parkButtonText = font.render("PARK THIS CAR" if car["parking"] == None else "UNPARK THIS CAR", True, "black")
            parkButtonTextPosition = parkButtonText.get_rect(x=(WIDTH-10-parkButtonText.get_width())//2, y=sectionStart[1]+60)
            pygame.draw.polygon(appScreen, "azure4", (parkButtonTextPosition.topleft, parkButtonTextPosition.topright, parkButtonTextPosition.bottomright, parkButtonTextPosition.bottomleft))           
            appScreen.blit(parkButtonText, parkButtonTextPosition)

            if parkButtonTextPosition.collidepoint(mouse_pos[0], mouse_pos[1]):
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                if left:
                    if car["parking"] == None:
                        dropdownSelectorChoice = None
                        dropdownSelector(list(doc.id for doc in getCollection()))
                        if dropdownSelectorChoice != None:
                            car["parking"] = dropdownSelectorChoice
                            parkingData = getDocument(dropdownSelectorChoice)
                            start = parkingData["start"]
                            start.append(f"{username}${car["id"]}")
                            updateDocument(dropdownSelectorChoice, {"start" : start})
                            updateDocument(username, {"userCars" : userCars}, "users")
                    else:  
                        parkingData = getDocument(car["parking"])
                        end = parkingData["end"]
                        for key in parkingData:
                            if parkingData[key] == f"{username}${car["id"]}":
                                end.append(key)
                        updateDocument(car["parking"], {"end" : end})
                        car["parking"] = None
                        updateDocument(username, {"userCars" : userCars}, "users")             

    elif selectedScreen == 2:
        debugText = font.render("DEBUG: ACCOUNT MANAGMENT", True, "black")
        debugTextPosition = debugText.get_rect(x=0, y=0)
        appScreen.blit(debugText, debugTextPosition)

    # ──────────────────────────────
    # BOTTOM BAR DRAW
    # ──────────────────────────────

    pygame.draw.polygon(appScreen, BOTTOMBAR_COLOR, ((0, HEIGHT-BOTTOMBAR_HEIGHT), (WIDTH, HEIGHT-BOTTOMBAR_HEIGHT), (WIDTH, HEIGHT), (0, HEIGHT)))
    for i in range(BOTTOMBAR_OPTIONS):
        pygame.draw.circle(appScreen, BOTTOMBAR_OPTIONS_SELECTED_COLOR if i == selectedScreen else BOTTOMBAR_OPTIONS_BASE_COLOR, (WIDTH/(BOTTOMBAR_OPTIONS+1)*(i+1), HEIGHT-BOTTOMBAR_HEIGHT/2), BOTTOMBAR_OPTIONS_RADIUS)
    
    for i in range(BOTTOMBAR_OPTIONS):
        if left and math.sqrt((WIDTH/(BOTTOMBAR_OPTIONS+1)*(i+1)-mouse_pos[0])**2+(HEIGHT-BOTTOMBAR_HEIGHT/2-mouse_pos[1])**2) <= BOTTOMBAR_OPTIONS_RADIUS:
            selectedScreen = i

    # ──────────────────────────────
    # WINDOW UPDATING
    # ──────────────────────────────

    pygame.display.flip()

pygame.quit()