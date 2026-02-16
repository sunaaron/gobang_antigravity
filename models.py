import pygame as pg
from typing import List, Tuple, Optional
from constants import GRID_SIZE, OFFSET, CELL_SIZE, STATE_MENU, STATE_PLAYING, MODE_PVP, PLAYER_BLACK

class GameObject:
    def __init__(self, image: pg.Surface, color_key: str, pos: Tuple[int, int]):
        self.image = image
        self.color_key = color_key
        self.rect = image.get_rect(center=pos)

class GameState:
    def __init__(self):
        self.board = [[' '] * GRID_SIZE for _ in range(GRID_SIZE)]
        self.history: List[GameObject] = []
        self.undone_history: List[GameObject] = []
        self.current_turn = 0  # 0 for Black, 1 for White
        self.winner: Optional[int] = None
        self.game_state = STATE_MENU
        self.game_mode = MODE_PVP
        self.player_color = PLAYER_BLACK
        self.scan_start_time = 0.0
        self.player_names = {0: "Player 1", 1: "Player 2"}
        self.selected_name_index = 0

    def reset(self):
        self.board = [[' '] * GRID_SIZE for _ in range(GRID_SIZE)]
        self.history.clear()
        self.undone_history.clear()
        self.current_turn = 0
        self.winner = None
        self.player_names = {0: "Player 1", 1: "Player 2"}

    def exit_to_menu(self):
        self.reset()
        self.game_state = STATE_MENU

    def get_state_data(self) -> dict:
        """Serializes current game state for synchronization."""
        return {
            'history': [(int(round((obj.rect.centerx - OFFSET) / CELL_SIZE)), 
                         int(round((obj.rect.centery - OFFSET) / CELL_SIZE))) 
                        for obj in self.history],
            'undone_history': [(int(round((obj.rect.centerx - OFFSET) / CELL_SIZE)), 
                                int(round((obj.rect.centery - OFFSET) / CELL_SIZE))) 
                               for obj in self.undone_history],
            'current_turn': self.current_turn,
            'winner': self.winner,
            'player_names': {str(k): v for k, v in self.player_names.items()}
        }

    def sync_from_data(self, data: dict, black_img: pg.Surface, white_img: pg.Surface):
        """Reconstructs state from serialized data."""
        self.board = [[' '] * GRID_SIZE for _ in range(GRID_SIZE)]
        self.history.clear()
        self.undone_history.clear()
        
        # Restore history
        for bx, by in data['history']:
            color_key = ['X', 'O'][len(self.history) % 2]
            self.board[by][bx] = color_key
            img = [black_img, white_img][len(self.history) % 2]
            pos = (OFFSET + bx * CELL_SIZE, OFFSET + by * CELL_SIZE)
            self.history.append(GameObject(img, color_key, pos))
            
        # Restore undone history (simple coordinates)
        # Note: We don't strictly need to reconstruct the full undone history objects 
        # unless we plan to redo from them locally, but let's do it for consistency.
        current_len = len(self.history)
        for i, (bx, by) in enumerate(data['undone_history']):
            # This is tricky because we need to know what color they were.
            # Alternating colors but we need to know the starting color for the stack.
            # For now, let's just store them as simplified objects or just skip full reconstruction 
            # if we trust the authoritative sync.
            pass

        self.current_turn = data['current_turn']
        self.winner = data['winner']
        if 'player_names' in data:
            # Convert string keys back to int
            self.player_names = {int(k): v for k, v in data['player_names'].items()}

    def place_stone(self, x: int, y: int, stone_image: pg.Surface) -> bool:
        if self.board[y][x] == ' ' and self.winner is None:
            color_key = ['X', 'O'][self.current_turn]
            self.board[y][x] = color_key
            pos = (OFFSET + x * CELL_SIZE, OFFSET + y * CELL_SIZE)
            self.history.append(GameObject(stone_image, color_key, pos))
            self.undone_history.clear()
            
            if self.check_win(x, y):
                self.winner = self.current_turn
            else:
                self.current_turn = 1 - self.current_turn
            return True
        return False

    def evaluate_move(self, x: int, y: int, player_char: str) -> int:
        score = 0
        opponent_char = 'X' if player_char == 'O' else 'O'
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
        
        for dx, dy in directions:
            for start_offset in range(-4, 1):
                window = []
                for i in range(5):
                    nx, ny = x + dx * (start_offset + i), y + dy * (start_offset + i)
                    if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
                        window.append(self.board[ny][nx])
                    else:
                        break
                
                if len(window) == 5:
                    count_p = window.count(player_char)
                    count_o = window.count(opponent_char)
                    
                    if count_p > 0 and count_o == 0:
                        if count_p == 4: score += 1000000 # Win
                        elif count_p == 3: score += 10000
                        elif count_p == 2: score += 1000
                    elif count_o > 0 and count_p == 0:
                        if count_o == 4: score += 900000 # Critical Block
                        elif count_o == 3: score += 8000
                        elif count_o == 2: score += 500
        return score

    def get_best_move(self) -> Optional[Tuple[int, int]]:
        import random
        best_score = -1
        moves = []
        
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                if self.board[y][x] == ' ':
                    score = self.evaluate_move(x, y, 'O') + self.evaluate_move(x, y, 'X')
                    if score > best_score:
                        best_score = score
                        moves = [(x, y)]
                    elif score == best_score:
                        moves.append((x, y))
        
        return random.choice(moves) if moves else None

    def undo(self) -> bool:
        from constants import MODE_PVC
        if not self.history:
            return False

        # If in PVC mode, we usually want to undo 2 moves (Player + CPU)
        # unless only one move has been played or it's game over.
        steps_to_undo = 1
        if self.game_mode == MODE_PVC and len(self.history) >= 2 and self.winner is None:
            steps_to_undo = 2

        for _ in range(steps_to_undo):
            if self.history:
                last_stone = self.history.pop()
                bx = int(round((last_stone.rect.centerx - OFFSET) / CELL_SIZE))
                by = int(round((last_stone.rect.centery - OFFSET) / CELL_SIZE))
                self.board[by][bx] = ' '
                self.undone_history.append(last_stone)
                self.current_turn = 1 - self.current_turn
        
        self.winner = None
        return True

    def redo(self) -> bool:
        if self.undone_history:
            stone = self.undone_history.pop()
            bx = int(round((stone.rect.centerx - OFFSET) / CELL_SIZE))
            by = int(round((stone.rect.centery - OFFSET) / CELL_SIZE))
            self.board[by][bx] = stone.color_key
            self.history.append(stone)
            if self.check_win(bx, by):
                self.winner = self.current_turn
            else:
                self.current_turn = 1 - self.current_turn
            return True
        return False

    def check_win(self, x: int, y: int) -> bool:
        color = self.board[y][x]
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
        for dx, dy in directions:
            count = 1
            # Check one direction
            for i in range(1, 5):
                nx, ny = x + dx * i, y + dy * i
                if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE and self.board[ny][nx] == color:
                    count += 1
                else:
                    break
            # Check opposite direction
            for i in range(1, 5):
                nx, ny = x - dx * i, y - dy * i
                if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE and self.board[ny][nx] == color:
                    count += 1
                else:
                    break
            if count >= 5:
                return True
        return False
