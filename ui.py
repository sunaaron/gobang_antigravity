import pygame as pg
from typing import Tuple

class Button:
    def __init__(self, text: str, color: Tuple[int, int, int], font: pg.font.Font, x: int, y: int):
        self.text = text
        self.color = color
        self.font = font
        self.surface = font.render(text, True, color)
        self.rect = self.surface.get_rect(topleft=(x, y))

    def is_clicked(self, pos: Tuple[int, int]) -> bool:
        return self.rect.collidepoint(pos)

    def draw(self, screen: pg.Surface):
        # Draw a subtle background for the button
        bg_rect = self.rect.inflate(20, 10)
        pg.draw.rect(screen, (50, 50, 60), bg_rect, border_radius=5)
        pg.draw.rect(screen, (100, 100, 110), bg_rect, width=1, border_radius=5)
        screen.blit(self.surface, self.rect)
