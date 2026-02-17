from constants import STATE_NAME_INPUT, STATE_LAN_MENU, STATE_PLAYING, PLAYER_BLACK, PLAYER_WHITE

def on_connection_established(game):
    """Called when a LAN connection is established (both host and client)."""
    if game.network_manager.is_host:
        # Host sends initial authoritative state including names
        game.network_manager.send_data({
            'type': 'sync_state',
            'state': game.state.get_state_data()
        })
        print("Host: Connection established. Initial state sent.")

def on_connection_lost(game):
    """Called when the LAN connection is dropped."""
    print("LAN: Connection lost. Returning to main menu.")
    game.network_manager.stop()
    game.state.exit_to_menu()

def on_remote_data_received(game, data: dict):
    """Callback for receiving moves or state sync from the network."""
    if data.get('type') == 'sync_state':
        # ONLY clients accept authoritative state from host
        if not game.network_manager.is_host:
            game.state.sync_from_data(data['state'], game.black_img, game.white_img)
            print(f"Client: Synced from Host. Turn: {['BLACK','WHITE'][game.state.current_turn]}, Names: {game.state.player_names}")
    elif data.get('type') == 'name_update':
        idx = data['player_index']
        name = data['name']
        game.state.player_names[idx] = name
        print(f"LAN: Remote name update: Player {idx+1} is {name}. Current names: {game.state.player_names}")
        # If host, broadcast the updated state to everyone (authorized change)
        if game.network_manager.is_host:
            game.network_manager.send_data({
                'type': 'sync_state',
                'state': game.state.get_state_data()
            })
    elif data.get('type') == 'move':
        # Processes incoming move
        bx, by = data['x'], data['y']
        print(f"Host: Received move from client: ({bx}, {by}). Current turn: {['BLACK','WHITE'][game.state.current_turn]}")
        if game.state.game_state == STATE_PLAYING:
            stone_img = [game.black_img, game.white_img][game.state.current_turn]
            if game.state.place_stone(bx, by, stone_img):
                print(f"Host: Successfully placed stone at ({bx}, {by}). Broadcasting authoritative state.")
                # If host, broadcast final authoritative state
                if game.network_manager.is_host:
                    game.network_manager.send_data({
                        'type': 'sync_state',
                        'state': game.state.get_state_data()
                    })
            else:
                print(f"Host: FAILED to place stone at ({bx}, {by}). Board might be occupied or game over.")
