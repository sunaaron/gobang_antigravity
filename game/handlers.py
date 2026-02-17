import time
from typing import Tuple
from constants import (STATE_MENU, STATE_PVC_CONFIG, STATE_LAN_MENU, STATE_PLAYING, STATE_NAME_INPUT,
                       MODE_PVP, MODE_PVC, MODE_LAN, PLAYER_BLACK, PLAYER_WHITE, 
                       OFFSET, CELL_SIZE, GRID_SIZE, SCAN_TIMEOUT, PREFILLED_NAMES)

def handle_click(game, pos: Tuple[int, int]):
    if game.state.game_state == STATE_MENU:
        handle_menu_click(game, pos)
    elif game.state.game_state == STATE_PVC_CONFIG:
        handle_pvc_config_click(game, pos)
    elif game.state.game_state == STATE_LAN_MENU:
        handle_lan_menu_click(game, pos)
    elif game.state.game_state == STATE_PLAYING:
        handle_playing_click(game, pos)

def handle_menu_click(game, pos: Tuple[int, int]):
    if game.renderer.menu_buttons['pvp'].is_clicked(pos):
        game.state.game_mode = MODE_PVP
        game.state.game_state = STATE_PLAYING
    elif game.renderer.menu_buttons['pvc'].is_clicked(pos):
        game.state.game_mode = MODE_PVC
        game.state.game_state = STATE_PVC_CONFIG
    elif game.renderer.menu_buttons['lan'].is_clicked(pos):
        game.state.game_mode = MODE_LAN
        game.state.game_state = STATE_LAN_MENU
        game.state.scan_start_time = time.time()
        game.network_manager.start_discovery_listener()
    elif game.renderer.menu_buttons['quit'].is_clicked(pos):
        game.running = False

def handle_lan_menu_click(game, pos: Tuple[int, int]):
    elapsed_time = time.time() - game.state.scan_start_time
    found_hosts = game.network_manager.found_hosts
    show_join = len(found_hosts) > 0
    show_new = not show_join and elapsed_time >= SCAN_TIMEOUT

    if show_new and game.renderer.lan_menu_buttons['new_game'].is_clicked(pos):
        game.state.reset()
        game.network_manager.stop_discovery()
        game.network_manager.start_server()
        game.network_manager.start_discovery_beacon()
        game.state.player_color = PLAYER_BLACK
        game.state.game_state = STATE_NAME_INPUT
        print("Host started. Entering name selection.")
    elif show_join and 'join' in game.renderer.lan_menu_buttons and game.renderer.lan_menu_buttons['join'].is_clicked(pos):
        host_ip = list(found_hosts)[0]
        if game.network_manager.connect_to_server(host_ip):
            game.state.reset()
            game.network_manager.stop_discovery()
            game.state.player_color = PLAYER_WHITE
            game.state.game_state = STATE_NAME_INPUT
            print(f"Joined host {host_ip}. Entering name selection.")
    elif game.renderer.lan_menu_buttons['back'].is_clicked(pos):
        game.network_manager.stop_discovery()
        game.state.game_state = STATE_MENU

def confirm_name(game):
    name = PREFILLED_NAMES[game.state.selected_name_index]
    game.state.player_names[game.state.player_color] = name
    game.state.game_state = STATE_PLAYING
    
    if game.state.game_mode == MODE_LAN:
        game.network_manager.send_data({
            'type': 'name_update',
            'player_index': game.state.player_color,
            'name': name
        })

def handle_pvc_config_click(game, pos: Tuple[int, int]):
    if game.renderer.pvc_config_buttons['black'].is_clicked(pos):
        game.state.player_color = PLAYER_BLACK
        game.state.player_names[PLAYER_BLACK] = "YOU"
        game.state.player_names[PLAYER_WHITE] = "CPU"
        game.state.game_state = STATE_PLAYING
    elif game.renderer.pvc_config_buttons['white'].is_clicked(pos):
        game.state.player_color = PLAYER_WHITE
        game.state.player_names[PLAYER_WHITE] = "YOU"
        game.state.player_names[PLAYER_BLACK] = "CPU"
        game.state.game_state = STATE_PLAYING
        game.handle_cpu_move() 
    elif game.renderer.pvc_config_buttons['back'].is_clicked(pos):
        game.state.game_state = STATE_MENU

def handle_playing_click(game, pos: Tuple[int, int]):
    if game.state.game_mode != MODE_LAN:
        if game.renderer.buttons['undo'].is_clicked(pos):
            if game.state.undo():
                if game.state.game_mode == MODE_PVC and game.state.current_turn != game.state.player_color and game.state.winner is None:
                    game.handle_cpu_move()
                return
        elif game.renderer.buttons['redo'].is_clicked(pos):
            if game.state.redo():
                return

    if game.renderer.buttons['restart'].is_clicked(pos):
        game.state.reset()
        if game.state.game_mode == MODE_PVC and game.state.player_color == PLAYER_WHITE:
            game.handle_cpu_move()
        elif game.state.game_mode == MODE_LAN:
            if game.network_manager.is_host:
                game.network_manager.send_data({
                    'type': 'sync_state',
                    'state': game.state.get_state_data()
                })
    elif game.renderer.buttons['exit'].is_clicked(pos):
        game.state.exit_to_menu()
        if game.state.game_mode == MODE_LAN:
            game.network_manager.stop()
    else:
        if game.state.game_mode in [MODE_PVC, MODE_LAN] and game.state.current_turn != game.state.player_color:
            return

        bx = int(round((pos[0] - OFFSET) / CELL_SIZE))
        by = int(round((pos[1] - OFFSET) / CELL_SIZE))
        
        if 0 <= bx < GRID_SIZE and 0 <= by < GRID_SIZE:
            stone_img = [game.black_img, game.white_img][game.state.current_turn]
            if game.state.place_stone(bx, by, stone_img):
                if game.state.game_mode == MODE_LAN:
                    if game.network_manager.is_host:
                        game.network_manager.send_data({
                            'type': 'sync_state',
                            'state': game.state.get_state_data()
                        })
                    else:
                        game.network_manager.send_data({
                            'type': 'move',
                            'x': bx,
                            'y': by
                        })
                
                if game.state.game_mode == MODE_PVC and game.state.winner is None:
                    game.handle_cpu_move()
