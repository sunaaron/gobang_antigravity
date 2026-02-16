import pygame as pg
from typing import Set, List
from constants import WIDTH, HEIGHT, WHITE, BLACK, RED, GREEN, SCAN_TIMEOUT, PREFILLED_NAMES
from ui import Button
from .utils import draw_gradient

def draw_menu(renderer):
    draw_gradient(renderer.screen, (25, 25, 30), (45, 50, 65), WIDTH, HEIGHT)
    
    # Subtle grid
    for i in range(0, WIDTH, 40):
        pg.draw.line(renderer.screen, (35, 35, 45), (i, 0), (i, HEIGHT))
    for i in range(0, HEIGHT, 40):
        pg.draw.line(renderer.screen, (35, 35, 45), (0, i), (WIDTH, i))

    title = renderer.font_title.render("GOBANG", True, WHITE)
    title_rect = title.get_rect(center=(WIDTH // 2, 150))
    renderer.screen.blit(title, title_rect)
    
    # Center buttons
    for btn in renderer.menu_buttons.values():
        btn.rect.centerx = WIDTH // 2
        btn.draw(renderer.screen)

def draw_pvc_config(renderer):
    draw_gradient(renderer.screen, (25, 25, 30), (45, 50, 65), WIDTH, HEIGHT)
    
    # Subtle grid
    for i in range(0, WIDTH, 40):
        pg.draw.line(renderer.screen, (35, 35, 45), (i, 0), (i, HEIGHT))
    for i in range(0, HEIGHT, 40):
        pg.draw.line(renderer.screen, (35, 35, 45), (0, i), (WIDTH, i))

    title = renderer.font_title.render("SELECT SIDE", True, WHITE)
    title_rect = title.get_rect(center=(WIDTH // 2, 150))
    renderer.screen.blit(title, title_rect)
    
    for btn in renderer.pvc_config_buttons.values():
        btn.rect.centerx = WIDTH // 2
        btn.draw(renderer.screen)

def draw_lan_menu(renderer, found_hosts: Set[str], elapsed_time: float):
    draw_gradient(renderer.screen, (20, 40, 60), (40, 80, 120), WIDTH, HEIGHT)
    
    title = renderer.font_title.render("LAN PLAY", True, WHITE)
    title_rect = title.get_rect(center=(WIDTH // 2, 150))
    renderer.screen.blit(title, title_rect)
    
    show_join = len(found_hosts) > 0
    show_new = not show_join and elapsed_time >= SCAN_TIMEOUT
    
    # Discovery Status
    if show_join:
        host_ip = list(found_hosts)[0]
        status_text = f"FOUND HOST: {host_ip}"
        status_color = GREEN
        if 'join' not in renderer.lan_menu_buttons:
            renderer.lan_menu_buttons['join'] = Button('JOIN GAME', GREEN, renderer.font_large, WIDTH // 2 - 100, 220)
    elif not show_new:
        remaining = max(0, int(SCAN_TIMEOUT - elapsed_time))
        status_text = f"Scanning for hosts... [{remaining}]"
        status_color = (180, 180, 180)
    else:
        status_text = "No hosts discovered."
        status_color = RED
        
    status_surf = renderer.font_medium.render(status_text, True, status_color)
    status_rect = status_surf.get_rect(center=(WIDTH // 2, 210))
    renderer.screen.blit(status_surf, status_rect)
    
    # Position buttons dynamically
    y_offset = 300
    visible_keys = ['back']
    if show_join: visible_keys.insert(0, 'join')
    elif show_new: visible_keys.insert(0, 'new_game')
    
    for key in visible_keys:
        if key in renderer.lan_menu_buttons:
            btn = renderer.lan_menu_buttons[key]
            btn.rect.center = (WIDTH // 2, y_offset)
            btn.draw(renderer.screen)
            y_offset += 80

def draw_name_input(renderer, state):
    draw_gradient(renderer.screen, (20, 20, 30), (40, 40, 60), WIDTH, HEIGHT)
    
    title = renderer.font_large.render("SELECT YOUR NAME", True, WHITE)
    title_rect = title.get_rect(center=(WIDTH // 2, 100))
    renderer.screen.blit(title, title_rect)
    
    y_start = 200
    for i, name in enumerate(PREFILLED_NAMES):
        color = WHITE
        is_selected = (i == state.selected_name_index)
        
        if is_selected:
            color = GREEN
            # Draw selection indicator
            indicator = renderer.font_medium.render(">", True, GREEN)
            renderer.screen.blit(indicator, (WIDTH // 2 - 100, y_start + i * 50))
        
        name_surf = renderer.font_medium.render(name, True, color)
        name_rect = name_surf.get_rect(center=(WIDTH // 2, y_start + i * 50 + 15))
        renderer.screen.blit(name_surf, name_rect)
    
    instruction = renderer.font_small.render("Use UP/DOWN to select, ENTER to confirm", True, (180, 180, 180))
    inst_rect = instruction.get_rect(center=(WIDTH // 2, HEIGHT - 100))
    renderer.screen.blit(instruction, inst_rect)
