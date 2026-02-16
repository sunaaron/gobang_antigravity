import pygame as pg
import time
from typing import Tuple
from constants import (WIDTH, HEIGHT, BLACK_CHESS, WHITE_CHESS, 
                       STATE_MENU, STATE_PVC_CONFIG, STATE_LAN_MENU, 
                       STATE_PLAYING, STATE_NAME_INPUT, PREFILLED_NAMES)
from models import GameState
from renderer import Renderer
from network import NetworkManager

# Import modular components
from .handlers import handle_click, confirm_name
from .network_callbacks import on_connection_established, on_connection_lost, on_remote_data_received
from .ai import handle_cpu_move

class GobangGame:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption("Gobang")
        
        self.black_img = pg.image.load(BLACK_CHESS).convert_alpha()
        self.white_img = pg.image.load(WHITE_CHESS).convert_alpha()
        
        self.state = GameState()
        self.renderer = Renderer(self.screen)
        self.network_manager = NetworkManager()
        
        # Rig callbacks
        self.network_manager.on_data_received = lambda data: on_remote_data_received(self, data)
        self.network_manager.on_connection_established = lambda: on_connection_established(self)
        self.network_manager.on_connection_lost = lambda: on_connection_lost(self)
        
        self.clock = pg.time.Clock()
        self.running = True

    def run(self):
        from constants import MODE_LAN
        while self.running:
            self.handle_events()
            
            network_info = None
            elapsed_scan_time = 0.0
            if self.state.game_state == STATE_LAN_MENU:
                elapsed_scan_time = time.time() - self.state.scan_start_time
            
            if self.state.game_mode == MODE_LAN:
                if self.network_manager.is_host:
                    ip = self.network_manager.get_local_ip()
                    network_info = f"IP: {ip}"
                elif self.network_manager.client_socket:
                    network_info = "CONNECTED"
                
            self.renderer.draw(self.state, network_info, self.network_manager.found_hosts, elapsed_scan_time)
            pg.display.update()
            self.clock.tick(60)
        pg.quit()

    def handle_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False
            elif event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                self.running = False
            elif event.type == pg.MOUSEBUTTONDOWN:
                pos = pg.mouse.get_pos()
                handle_click(self, pos)
            elif self.state.game_state == STATE_NAME_INPUT:
                if event.type == pg.KEYDOWN:
                    if event.key in [pg.K_RETURN, pg.K_KP_ENTER]:
                        confirm_name(self)
                    elif event.key == pg.K_UP:
                        self.state.selected_name_index = (self.state.selected_name_index - 1) % len(PREFILLED_NAMES)
                    elif event.key == pg.K_DOWN:
                        self.state.selected_name_index = (self.state.selected_name_index + 1) % len(PREFILLED_NAMES)

    def handle_cpu_move(self):
        handle_cpu_move(self)
