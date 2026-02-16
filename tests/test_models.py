import unittest
import pygame as pg
from models import GameState, GameObject
from constants import GRID_SIZE, PLAYER_BLACK, PLAYER_WHITE, MODE_PVP

class TestGameState(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pg.init()
        # Mocking images for stones
        cls.mock_img = pg.Surface((20, 20))

    def setUp(self):
        self.state = GameState()

    def test_initial_state(self):
        self.assertEqual(len(self.state.board), GRID_SIZE)
        self.assertEqual(self.state.current_turn, 0)
        self.assertIsNone(self.state.winner)

    def test_stone_placement(self):
        self.assertTrue(self.state.place_stone(7, 7, self.mock_img))
        self.assertEqual(self.state.board[7][7], 'X')
        self.assertEqual(self.state.current_turn, 1)

    def test_invalid_stone_placement(self):
        self.state.place_stone(7, 7, self.mock_img)
        self.assertFalse(self.state.place_stone(7, 7, self.mock_img))

    def test_horizontal_win(self):
        for i in range(5):
            self.state.place_stone(i, 0, self.mock_img) # Black
            if i < 4:
                self.state.place_stone(i, 1, self.mock_img) # White
        self.assertEqual(self.state.winner, 0)

    def test_undo_redo(self):
        self.state.place_stone(7, 7, self.mock_img)
        self.state.undo()
        self.assertEqual(self.state.board[7][7], ' ')
        self.state.redo()
        self.assertEqual(self.state.board[7][7], 'X')

    def test_ai_scoring_immediate_win(self):
        # Set up 4 in a row for CPU (O)
        for i in range(4):
            self.state.board[0][i] = 'O'
        # Evaluate winning move
        score = self.state.evaluate_move(4, 0, 'O')
        self.assertGreaterEqual(score, 1000000)

    def test_ai_scoring_critical_block(self):
        # Set up 4 in a row for Player (X)
        for i in range(4):
            self.state.board[0][i] = 'X'
        # Evaluate blocking move for CPU (O)
        score = self.state.evaluate_move(4, 0, 'O')
        self.assertGreaterEqual(score, 900000)

if __name__ == '__main__':
    unittest.main()
