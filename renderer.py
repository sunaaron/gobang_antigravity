import pygame as pg
from typing import Optional, Set
from constants import WIDTH, HEIGHT, BLACK, WHITE, RED, BLUE, GREEN, BG_IMG, TITLE_FONT_PATH, MENU_FONT_PATH, STATE_MENU, STATE_PLAYING, STATE_PVC_CONFIG, STATE_LAN_MENU, STATE_NAME_INPUT
from models import GameState
from ui import Button

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
            self.draw_menu()
        elif state.game_state == STATE_PVC_CONFIG:
            self.draw_pvc_config()
        elif state.game_state == STATE_LAN_MENU:
            self.draw_lan_menu(found_hosts or set(), elapsed_time)
        elif state.game_state == STATE_NAME_INPUT:
            self.draw_name_input(state)
        elif state.game_state == STATE_PLAYING:
            # Clear screen completely (especially for sidebar area not covered by board bg)
            self.screen.fill((30, 30, 40))
            
            if self.bg is None:
                self.bg = pg.image.load(BG_IMG).convert_alpha()
            self.screen.blit(self.bg, (0, 0))
            self.draw_game(state, network_info)

    def draw_lan_menu(self, found_hosts: Set[str], elapsed_time: float):
        from constants import SCAN_TIMEOUT
        self._draw_gradient((20, 40, 60), (40, 80, 120))
        
        title = self.font_title.render("LAN PLAY", True, WHITE)
        title_rect = title.get_rect(center=(WIDTH // 2, 150))
        self.screen.blit(title, title_rect)
        
        show_join = len(found_hosts) > 0
        show_new = not show_join and elapsed_time >= SCAN_TIMEOUT
        
        # Discovery Status
        if show_join:
            host_ip = list(found_hosts)[0]
            status_text = f"FOUND HOST: {host_ip}"
            status_color = GREEN
            if 'join' not in self.lan_menu_buttons:
                self.lan_menu_buttons['join'] = Button('JOIN GAME', GREEN, self.font_large, WIDTH // 2 - 100, 220)
        elif not show_new:
            remaining = max(0, int(SCAN_TIMEOUT - elapsed_time))
            status_text = f"Scanning for hosts... [{remaining}]"
            status_color = (180, 180, 180)
        else:
            status_text = "No hosts discovered."
            status_color = RED
            
        status_surf = self.font_medium.render(status_text, True, status_color)
        status_rect = status_surf.get_rect(center=(WIDTH // 2, 210))
        self.screen.blit(status_surf, status_rect)
        
        # Position buttons dynamically
        y_offset = 300
        visible_keys = ['back']
        if show_join: visible_keys.insert(0, 'join')
        elif show_new: visible_keys.insert(0, 'new_game')
        
        for key in visible_keys:
            if key in self.lan_menu_buttons:
                btn = self.lan_menu_buttons[key]
                btn.rect.center = (WIDTH // 2, y_offset)
                btn.draw(self.screen)
                y_offset += 80

    def draw_pvc_config(self):
        self._draw_gradient((25, 25, 30), (45, 50, 65))
        
        # Subtle grid
        for i in range(0, WIDTH, 40):
            pg.draw.line(self.screen, (35, 35, 45), (i, 0), (i, HEIGHT))
        for i in range(0, HEIGHT, 40):
            pg.draw.line(self.screen, (35, 35, 45), (0, i), (WIDTH, i))

        title = self.font_title.render("SELECT SIDE", True, WHITE)
        title_rect = title.get_rect(center=(WIDTH // 2, 150))
        self.screen.blit(title, title_rect)
        
        for btn in self.pvc_config_buttons.values():
            btn.rect.centerx = WIDTH // 2
            btn.draw(self.screen)

    def draw_menu(self):
        self._draw_gradient((25, 25, 30), (45, 50, 65))
        
        # Subtle grid
        for i in range(0, WIDTH, 40):
            pg.draw.line(self.screen, (35, 35, 45), (i, 0), (i, HEIGHT))
        for i in range(0, HEIGHT, 40):
            pg.draw.line(self.screen, (35, 35, 45), (0, i), (WIDTH, i))

        title = self.font_title.render("GOBANG", True, WHITE)
        title_rect = title.get_rect(center=(WIDTH // 2, 150))
        self.screen.blit(title, title_rect)
        
        # Center buttons
        for btn in self.menu_buttons.values():
            btn.rect.centerx = WIDTH // 2
            btn.draw(self.screen)

    def _draw_gradient(self, color1, color2):
        for y in range(HEIGHT):
            r = color1[0] + (color2[0] - color1[0]) * y // HEIGHT
            g = color1[1] + (color2[1] - color1[1]) * y // HEIGHT
            b = color1[2] + (color2[2] - color1[2]) * y // HEIGHT
            pg.draw.line(self.screen, (r, g, b), (0, y), (WIDTH, y))

    def draw_game(self, state: GameState, network_info: Optional[str] = None):
        from constants import GRID_SIZE, CELL_SIZE, OFFSET, MODE_LAN, PLAYER_BLACK, PLAYER_WHITE
        # Draw stones
        for stone in state.history:
            self.screen.blit(stone.image, stone.rect)
            
        # Draw UI
        from constants import MODE_LAN
        visible_keys = []
        for key in ['undo', 'redo', 'restart', 'exit']:
            if state.game_mode == MODE_LAN and key in ['undo', 'redo']:
                continue
            visible_keys.append(key)
            
        # Center them vertically in the sidebar area
        start_y = 150 if len(visible_keys) > 2 else 250
        spacing = 100
        for i, key in enumerate(visible_keys):
            btn = self.buttons[key]
            btn.rect.centery = start_y + i * spacing
            btn.draw(self.screen)
            
        # Connection Info at top right of sidebar
        if state.game_mode == MODE_LAN and network_info:
            info_text = self.font_small.render(network_info, True, (200, 200, 200))
        else:
            info_text = self.font_small.render("Local game", True, (150, 150, 150))
        
        # Position above UNDO button
        # Sidebar center shifted to ~745
        self.screen.blit(info_text, (745 - info_text.get_width() // 2, 70))
        
        # Player Names
        p1_display = state.player_names[0]
        p2_display = state.player_names[1]
        
        # In LAN mode, show waiting if peer name is just the default
        if state.game_mode == MODE_LAN:
            # Robust check for default names
            p1_default = p1_display.strip().lower() in ["player 1", "player 1", ""]
            p2_default = p2_display.strip().lower() in ["player 2", "player 2", ""]
            
            if state.player_color == PLAYER_BLACK and p2_default:
                p2_display = "Waiting..."
            elif state.player_color == PLAYER_WHITE and p1_default:
                p1_display = "Waiting..."
            
        # Use light gray (220, 220, 220) instead of pure BLACK for visibility on dark BG
        name1_color = (220, 220, 220) if state.current_turn == 0 else (100, 100, 100)
        name2_color = WHITE if state.current_turn == 1 else (150, 150, 150)
        
        name1 = self.font_medium.render(p1_display, True, name1_color)
        name2 = self.font_medium.render(p2_display, True, name2_color)
        self.screen.blit(name1, (745 - name1.get_width() // 2, 120))
        self.screen.blit(name2, (745 - name2.get_width() // 2, 160))
        
        # Authoritative Turn Indicator (at top center of board)
        current_name = state.player_names[state.current_turn]
        turn_color = (220, 220, 220) if state.current_turn == 0 else WHITE
        status = self.font_small.render(f"{current_name}'s TURN", True, turn_color)
        board_center_x = (GRID_SIZE - 1) * CELL_SIZE // 2 + OFFSET
        self.screen.blit(status, (board_center_x - status.get_width() // 2, 2))
        
        if state.winner is not None:
            win_text = self.font_medium.render(f"{state.player_names[state.winner]} WINS!", True, RED)
            self.screen.blit(win_text, (board_center_x - win_text.get_width() // 2, 200))

    def draw_name_input(self, state: GameState):
        from constants import WIDTH, HEIGHT, WHITE, BLACK, GREEN, PREFILLED_NAMES
        self._draw_gradient((20, 20, 30), (40, 40, 60))
        
        title = self.font_large.render("SELECT YOUR NAME", True, WHITE)
        title_rect = title.get_rect(center=(WIDTH // 2, 100))
        self.screen.blit(title, title_rect)
        
        y_start = 200
        for i, name in enumerate(PREFILLED_NAMES):
            color = WHITE
            is_selected = (i == state.selected_name_index)
            
            if is_selected:
                color = GREEN
                # Draw selection indicator
                indicator = self.font_medium.render(">", True, GREEN)
                self.screen.blit(indicator, (WIDTH // 2 - 100, y_start + i * 50))
            
            name_surf = self.font_medium.render(name, True, color)
            name_rect = name_surf.get_rect(center=(WIDTH // 2, y_start + i * 50 + 15))
            self.screen.blit(name_surf, name_rect)
        
        instruction = self.font_small.render("Use UP/DOWN to select, ENTER to confirm", True, (180, 180, 180))
        inst_rect = instruction.get_rect(center=(WIDTH // 2, HEIGHT - 100))
        self.screen.blit(instruction, inst_rect)
