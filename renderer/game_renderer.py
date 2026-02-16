import pygame as pg
from typing import Optional
from constants import GRID_SIZE, CELL_SIZE, OFFSET, MODE_LAN, PLAYER_BLACK, PLAYER_WHITE, DARK_RED, WHITE, RED
from models import GameState

def draw_game(renderer, state: GameState, network_info: Optional[str] = None):
    # Draw stones
    for stone in state.history:
        renderer.screen.blit(stone.image, stone.rect)
        
    # Draw indicator for the latest move
    if state.history:
        last_stone = state.history[-1]
        pg.draw.circle(renderer.screen, DARK_RED, last_stone.rect.center, 5)

    # Draw UI
    visible_keys = []
    for key in ['undo', 'redo', 'restart', 'exit']:
        if state.game_mode == MODE_LAN and key in ['undo', 'redo']:
            continue
        visible_keys.append(key)
        
    # Center them vertically in the sidebar area
    start_y = 150 if len(visible_keys) > 2 else 250
    spacing = 100
    for i, key in enumerate(visible_keys):
        btn = renderer.buttons[key]
        btn.rect.centery = start_y + i * spacing
        btn.draw(renderer.screen)
        
    # Connection Info at top right of sidebar
    if state.game_mode == MODE_LAN and network_info:
        info_text = renderer.font_small.render(network_info, True, (200, 200, 200))
    else:
        info_text = renderer.font_small.render("Local game", True, (150, 150, 150))
    
    # Position above UNDO button
    # Sidebar center shifted to ~745
    renderer.screen.blit(info_text, (745 - info_text.get_width() // 2, 70))
    
    # Player Names
    p1_display = state.player_names[0]
    p2_display = state.player_names[1]
    
    # In LAN mode, show waiting if peer name is just the default
    if state.game_mode == MODE_LAN:
        # Robust check for default names (case-insensitive)
        p1_default = p1_display.strip().lower() in ["player 1", ""]
        p2_default = p2_display.strip().lower() in ["player 2", ""]
        
        if state.player_color == PLAYER_BLACK and p2_default:
            p2_display = "Waiting..."
        elif state.player_color == PLAYER_WHITE and p1_default:
            p1_display = "Waiting..."
        
    # Use light gray (220, 220, 220) instead of pure BLACK for visibility on dark BG
    name1_color = (220, 220, 220) if state.current_turn == 0 else (100, 100, 100)
    name2_color = WHITE if state.current_turn == 1 else (150, 150, 150)
    
    if state.game_mode == MODE_LAN:
        name1 = renderer.font_medium.render(p1_display, True, name1_color)
        name2 = renderer.font_medium.render(p2_display, True, name2_color)
        renderer.screen.blit(name1, (745 - name1.get_width() // 2, 120))
        renderer.screen.blit(name2, (745 - name2.get_width() // 2, 160))
    
    # Authoritative Turn Indicator (at top center of board)
    current_name = state.player_names[state.current_turn]
    turn_color = (220, 220, 220) if state.current_turn == 0 else WHITE
    status = renderer.font_small.render(f"{current_name}'s TURN", True, turn_color)
    board_center_x = (GRID_SIZE - 1) * CELL_SIZE // 2 + OFFSET
    renderer.screen.blit(status, (board_center_x - status.get_width() // 2, 2))
    
    if state.winner is not None:
        win_text = renderer.font_medium.render(f"{state.player_names[state.winner]} WINS!", True, RED)
        renderer.screen.blit(win_text, (board_center_x - win_text.get_width() // 2, 200))
