import pygame as pg


pg.display.init()
pg.font.init()

WIN_H = 1000
WIN_W = 1000
WIN = pg.display.set_mode((WIN_W, WIN_H), pg.SCALED | pg.NOFRAME)

FPS = 60

FONT_1 = pg.sysfont.SysFont("console", 24)