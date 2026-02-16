import pygame as pg
from typing import Optional, Set
from constants import (WIDTH, HEIGHT, BG_IMG, TITLE_FONT_PATH, MENU_FONT_PATH, 
                       STATE_MENU, STATE_PLAYING, STATE_PVC_CONFIG, 
                       STATE_LAN_MENU, STATE_NAME_INPUT, BLUE, GREEN, RED, BLACK, WHITE)
from models import GameState
from ui import Button

# Import specialized renderers
from .menu_renderer import draw_menu, draw_pvc_config, draw_lan_menu, draw_name_input
from .game_renderer import draw_game

class Renderer:
    def __init__(self, screen: pg.Surface):
        self.screen = screen
        self.bg = None
        self.font_small = pg.font.Font(MENU_FONT_PATH, 20)
        self.font_medium = pg.font.Font(MENU_FONT_PATH, 25)
        self.font_large = pg.font.Font(MENU_FONT_PATH, 30)
        self.font_title = pg.font.Font(TITLE_FONT_PATH, 60)
        
        self.buttons = {
            'undo': Button('UNDO', RED, self.font_medium, 700, 150),
            'redo': Button('REDO', BLUE, self.font_medium, 700, 250),
            'restart': Button('RESTART', GREEN, self.font_medium, 700, 350),
            'exit': Button('MENU', (120, 120, 120), self.font_medium, 700, 450)
        }

        self.menu_buttons = {
            'pvp': Button('PLAYER VS PLAYER', BLUE, self.font_large, WIDTH // 2 - 150, 200),
            'pvc': Button('PLAYER VS CPU', GREEN, self.font_large, WIDTH // 2 - 130, 270),
            'lan': Button('LAN PLAY', (200, 150, 50), self.font_large, WIDTH // 2 - 80, 340),
            'quit': Button('QUIT GAME', (120, 120, 120), self.font_large, WIDTH // 2 - 100, 410),
        }

        self.pvc_config_buttons = {
            'black': Button('PLAY AS BLACK', BLACK, self.font_large, WIDTH // 2 - 130, 250),
            'white': Button('PLAY AS WHITE', WHITE, self.font_large, WIDTH // 2 - 130, 320),
            'back': Button('BACK', (120, 120, 120), self.font_large, WIDTH // 2 - 60, 390),
        }

        self.lan_menu_buttons = {
            'new_game': Button('NEW GAME', GREEN, self.font_large, WIDTH // 2 - 100, 280),
            'back': Button('MENU', (120, 120, 120), self.font_large, WIDTH // 2 - 60, 350),
        }

    def draw(self, state: GameState, network_info: Optional[str] = None, found_hosts: Optional[Set[str]] = None, elapsed_time: float = 0.0):
        if state.game_state == STATE_MENU:
            draw_menu(self)
        elif state.game_state == STATE_PVC_CONFIG:
            draw_pvc_config(self)
        elif state.game_state == STATE_LAN_MENU:
            draw_lan_menu(self, found_hosts or set(), elapsed_time)
        elif state.game_state == STATE_NAME_INPUT:
            draw_name_input(self, state)
        elif state.game_state == STATE_PLAYING:
            # Clear screen completely
            self.screen.fill((30, 30, 40))
            
            if self.bg is None:
                self.bg = pg.image.load(BG_IMG).convert_alpha()
            self.screen.blit(self.bg, (0, 0))
            draw_game(self, state, network_info)
