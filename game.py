import pygame as pg
import time
from typing import Tuple
from constants import WIDTH, HEIGHT, BLACK_CHESS, WHITE_CHESS, OFFSET, CELL_SIZE, GRID_SIZE, STATE_MENU, STATE_PVC_CONFIG, STATE_LAN_MENU, STATE_PLAYING, STATE_NAME_INPUT, MODE_PVP, MODE_PVC, MODE_LAN, PLAYER_BLACK, PLAYER_WHITE
from models import GameState
from renderer import Renderer
from network import NetworkManager

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
        self.network_manager.on_data_received = self._on_remote_data_received
        self.network_manager.on_connection_established = self._on_connection_established
        self.network_manager.on_connection_lost = self._on_connection_lost
        
        self.clock = pg.time.Clock()
        self.running = True

    def run(self):
        from constants import MODE_LAN, DEFAULT_PORT
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
                self.handle_click(pos)
            elif self.state.game_state == STATE_NAME_INPUT:
                from constants import PREFILLED_NAMES
                if event.type == pg.KEYDOWN:
                    if event.key in [pg.K_RETURN, pg.K_KP_ENTER]:
                        self._confirm_name()
                    elif event.key == pg.K_UP:
                        self.state.selected_name_index = (self.state.selected_name_index - 1) % len(PREFILLED_NAMES)
                    elif event.key == pg.K_DOWN:
                        self.state.selected_name_index = (self.state.selected_name_index + 1) % len(PREFILLED_NAMES)

    def handle_click(self, pos: Tuple[int, int]):
        if self.state.game_state == STATE_MENU:
            self._handle_menu_click(pos)
        elif self.state.game_state == STATE_PVC_CONFIG:
            self._handle_pvc_config_click(pos)
        elif self.state.game_state == STATE_LAN_MENU:
            self._handle_lan_menu_click(pos)
        elif self.state.game_state == STATE_PLAYING:
            self._handle_playing_click(pos)

    def _handle_menu_click(self, pos: Tuple[int, int]):
        if self.renderer.menu_buttons['pvp'].is_clicked(pos):
            self.state.game_mode = MODE_PVP
            self.state.game_state = STATE_PLAYING
        elif self.renderer.menu_buttons['pvc'].is_clicked(pos):
            self.state.game_mode = MODE_PVC
            self.state.game_state = STATE_PVC_CONFIG
        elif self.renderer.menu_buttons['lan'].is_clicked(pos):
            self.state.game_mode = MODE_LAN
            self.state.game_state = STATE_LAN_MENU
            self.state.scan_start_time = time.time()
            self.network_manager.start_discovery_listener()
        elif self.renderer.menu_buttons['quit'].is_clicked(pos):
            self.running = False

    def _handle_lan_menu_click(self, pos: Tuple[int, int]):
        from constants import SCAN_TIMEOUT
        elapsed_time = time.time() - self.state.scan_start_time
        found_hosts = self.network_manager.found_hosts
        show_join = len(found_hosts) > 0
        show_new = not show_join and elapsed_time >= SCAN_TIMEOUT

        if show_new and self.renderer.lan_menu_buttons['new_game'].is_clicked(pos):
            self.state.reset()
            self.network_manager.stop_discovery()
            self.network_manager.start_server()
            self.network_manager.start_discovery_beacon()
            self.state.player_color = PLAYER_BLACK
            self.state.game_state = STATE_NAME_INPUT
            print("Host started. Entering name selection.")
        elif show_join and 'join' in self.renderer.lan_menu_buttons and self.renderer.lan_menu_buttons['join'].is_clicked(pos):
            host_ip = list(found_hosts)[0]
            if self.network_manager.connect_to_server(host_ip):
                self.state.reset()
                self.network_manager.stop_discovery()
                self.state.player_color = PLAYER_WHITE
                self.state.game_state = STATE_NAME_INPUT
                print(f"Joined host {host_ip}. Entering name selection.")
        elif self.renderer.lan_menu_buttons['back'].is_clicked(pos):
            self.network_manager.stop_discovery()
            self.state.game_state = STATE_MENU

    def _confirm_name(self):
        from constants import PREFILLED_NAMES
        name = PREFILLED_NAMES[self.state.selected_name_index]
        self.state.player_names[self.state.player_color] = name
        self.state.game_state = STATE_PLAYING
        
        # Broadcast name to peer
        if self.state.game_mode == MODE_LAN:
            self.network_manager.send_data({
                'type': 'name_update',
                'player_index': self.state.player_color,
                'name': name
            })
            # Also send existing names if any (though usually we just care about ours)
            # Actually, sending just ours is enough as the other will do the same.

    def _handle_pvc_config_click(self, pos: Tuple[int, int]):
        if self.renderer.pvc_config_buttons['black'].is_clicked(pos):
            self.state.player_color = PLAYER_BLACK
            self.state.game_state = STATE_PLAYING
        elif self.renderer.pvc_config_buttons['white'].is_clicked(pos):
            self.state.player_color = PLAYER_WHITE
            self.state.game_state = STATE_PLAYING
            self.handle_cpu_move() # CPU starts as Black
        elif self.renderer.pvc_config_buttons['back'].is_clicked(pos):
            self.state.game_state = STATE_MENU

    def _on_connection_established(self):
        """Called when a LAN connection is established (both host and client)."""
        if self.network_manager.is_host:
            # Host sends initial authoritative state including names
            self.network_manager.send_data({
                'type': 'sync_state',
                'state': self.state.get_state_data()
            })
            print("Host: Connection established. Initial state sent.")

    def _on_connection_lost(self):
        """Called when the LAN connection is dropped."""
        print("LAN: Connection lost. Returning to main menu.")
        self.network_manager.stop()
        self.state.exit_to_menu()

    def _on_remote_data_received(self, data: dict):
        """Callback for receiving moves or state sync from the network."""
        if data.get('type') == 'sync_state':
            # ONLY clients accept authoritative state from host
            if not self.network_manager.is_host:
                self.state.sync_from_data(data['state'], self.black_img, self.white_img)
                print(f"Client: Synced from Host. Turn: {['BLACK','WHITE'][self.state.current_turn]}, Names: {self.state.player_names}")
        elif data.get('type') == 'name_update':
            idx = data['player_index']
            name = data['name']
            self.state.player_names[idx] = name
            print(f"LAN: Remote name update: Player {idx+1} is {name}. Current names: {self.state.player_names}")
            # If host, broadcast the updated state to everyone (authorized change)
            if self.network_manager.is_host:
                self.network_manager.send_data({
                    'type': 'sync_state',
                    'state': self.state.get_state_data()
                })
        elif data.get('type') == 'move':
            # Processes incoming move
            bx, by = data['x'], data['y']
            print(f"Host: Received move from client: ({bx}, {by}). Current turn: {['BLACK','WHITE'][self.state.current_turn]}")
            if self.state.game_state == STATE_PLAYING:
                stone_img = [self.black_img, self.white_img][self.state.current_turn]
                if self.state.place_stone(bx, by, stone_img):
                    print(f"Host: Successfully placed stone at ({bx}, {by}). Broadcasting authoritative state.")
                    # If host, broadcast final authoritative state
                    if self.network_manager.is_host:
                        self.network_manager.send_data({
                            'type': 'sync_state',
                            'state': self.state.get_state_data()
                        })
                else:
                    print(f"Host: FAILED to place stone at ({bx}, {by}). Board might be occupied or game over.")

    def _handle_playing_click(self, pos: Tuple[int, int]):
        # Check game buttons
        if self.state.game_mode != MODE_LAN:
            if self.renderer.buttons['undo'].is_clicked(pos):
                if self.state.undo():
                    if self.state.game_mode == MODE_PVC and self.state.current_turn != self.state.player_color and self.state.winner is None:
                        self.handle_cpu_move()
                    return # Exit after handling button
            elif self.renderer.buttons['redo'].is_clicked(pos):
                if self.state.redo():
                    return # Exit after handling button

        if self.renderer.buttons['restart'].is_clicked(pos):
            self.state.reset()
            if self.state.game_mode == MODE_PVC and self.state.player_color == PLAYER_WHITE:
                self.handle_cpu_move()
            elif self.state.game_mode == MODE_LAN:
                if self.network_manager.is_host:
                    self.network_manager.send_data({
                        'type': 'sync_state',
                        'state': self.state.get_state_data()
                    })
                # Client shouldn't be able to trigger sync_state restart, 
                # maybe add 'request_restart' later if needed.
        elif self.renderer.buttons['exit'].is_clicked(pos):
            self.state.exit_to_menu()
            if self.state.game_mode == MODE_LAN:
                self.network_manager.stop()
        else:
            # In PVC or LAN, only allow clicking on local player's turn
            if self.state.game_mode in [MODE_PVC, MODE_LAN] and self.state.current_turn != self.state.player_color:
                return

            # Check grid
            bx = int(round((pos[0] - OFFSET) / CELL_SIZE))
            by = int(round((pos[1] - OFFSET) / CELL_SIZE))
            
            if 0 <= bx < GRID_SIZE and 0 <= by < GRID_SIZE:
                stone_img = [self.black_img, self.white_img][self.state.current_turn]
                if self.state.place_stone(bx, by, stone_img):
                    # After move, synchronize if in LAN mode
                    if self.state.game_mode == MODE_LAN:
                        if self.network_manager.is_host:
                            self.network_manager.send_data({
                                'type': 'sync_state',
                                'state': self.state.get_state_data()
                            })
                        else:
                            self.network_manager.send_data({
                                'type': 'move',
                                'x': bx,
                                'y': by
                            })
                    
                    # After player move in PVC, trigger CPU
                    if self.state.game_mode == MODE_PVC and self.state.winner is None:
                        self.handle_cpu_move()

    def handle_cpu_move(self):
        # The AI now evaluates the board to find the best move
        move = self.state.get_best_move()
        if move:
            bx, by = move
            stone_img = [self.black_img, self.white_img][self.state.current_turn]
            if self.state.place_stone(bx, by, stone_img):
                if self.state.winner is not None:
                    winner_name = ["BLACK", "WHITE"][self.state.winner]
                    print(f"Winner: CPU ({winner_name})")
