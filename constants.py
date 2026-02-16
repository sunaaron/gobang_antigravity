import pygame as pg

# Screen settings
WIDTH, HEIGHT = 850, 615
GRID_SIZE = 15
CELL_SIZE = 40
OFFSET = 27

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 48, 48)
DARK_RED = (180, 0, 0)
BLUE = (65, 105, 225)
GREEN = (0, 139, 0)

# Paths
DATA_DIR = "data"
TITLE_FONT_PATH = "font/game_title.TTF"
MENU_FONT_PATH = "font/game_menu.TTF"

# Assets
BG_IMG = f"{DATA_DIR}/bg.png"
BLACK_CHESS = f"{DATA_DIR}/chess_black.png"
WHITE_CHESS = f"{DATA_DIR}/chess_white.png"

# Game States
STATE_MENU = "MENU"
STATE_PVC_CONFIG = "PVC_CONFIG"
STATE_LAN_MENU = "LAN_MENU"
STATE_PLAYING = "PLAYING"
STATE_NAME_INPUT = "NAME_INPUT"

# Player Colors/Roles
PLAYER_BLACK = 0
PLAYER_WHITE = 1

# Game Modes
MODE_PVP = "PVP"
MODE_PVC = "PVC"
MODE_LAN = "LAN"

# Networking
DEFAULT_PORT = 5005
NET_BUFFER_SIZE = 1024
DISCOVERY_PORT = 5006
DISCOVERY_INTERVAL = 1.0  # seconds
SCAN_TIMEOUT = 7.0  # seconds

# Prefilled Names
PREFILLED_NAMES = ["Stella", "Sheryl", "Aaron", "Jessie"]
