import pygame as pg


pg.display.init()
pg.font.init()

WIN_H = 500 # 1080
WIN_W = 500 # 1920
WIN = pg.display.set_mode((WIN_W, WIN_H), pg.SCALED) # , pg.FULLSCREEN

FPS = 240

FONT_1 = pg.sysfont.SysFont("console", 24)