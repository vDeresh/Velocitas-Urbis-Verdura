import pygame as pg
import os


pg.display.init()
pg.font.init()

WIN_H = 1080 # 500
WIN_W = 1920 # 500
WIN = pg.display.set_mode((WIN_W, WIN_H), pg.SCALED, pg.FULLSCREEN)
SURF_MAIN = pg.Surface((WIN_W, WIN_H))

# FPS = 60

# FONT_1 = pg.sysfont.SysFont("console", 24)
# FONT_2 = pg.sysfont.SysFont("console", 16)


FONT_1 = pg.Font(os.path.join("src", "fonts", "MajorMonoDisplay", "MajorMonoDisplay-Regular.ttf"), 16)
FONT_2 = pg.Font(os.path.join("src", "fonts", "RubikMonoOne", "RubikMonoOne-Regular.ttf"), 16)
FONT_3 = pg.Font(os.path.join("src", "fonts", "RubikMonoOne", "RubikMonoOne-Regular.ttf"), 64)


COLOR_BACKGROUND = pg.Color(100, 110, 140)
COLOR_BACKGROUND_ALPHA_20 = pg.Color(100, 110, 140, 20)
COLOR_MONITOR = pg.Color(34, 32, 52)
COLOR_MONITOR_ALPHA_40 = pg.Color(34, 32, 52, 40)
COLOR_MONITOR_2 = pg.Color(26, 26, 44)
COLOR_MONITOR_2_ALPHA_40 = pg.Color(26, 26, 44, 40)