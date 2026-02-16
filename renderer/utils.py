import pygame as pg

def draw_gradient(screen, color1, color2, width, height):
    """Draws a vertical gradient from color1 to color2."""
    for y in range(height):
        r = color1[0] + (color2[0] - color1[0]) * y // height
        g = color1[1] + (color2[1] - color1[1]) * y // height
        b = color1[2] + (color2[2] - color1[2]) * y // height
        pg.draw.line(screen, (r, g, b), (0, y), (width, y))
