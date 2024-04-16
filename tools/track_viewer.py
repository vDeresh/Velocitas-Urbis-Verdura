import sys
import json
from os import path


def show():
    with open(path.abspath(path.join("src", "data", "tracks")), "r") as file:
        return json.load(file)


TRACK = show()[sys.argv[1]]['track']
TRACK_POINTS = []
for x, y, *_ in TRACK:
    TRACK_POINTS.append((x, y))

PITLANE = show()[sys.argv[1]]['pit-lane']
PITLANE_POINTS = []
for x, y, *_ in PITLANE:
    PITLANE_POINTS.append((x, y))


import pygame as pg

pg.font.init()
FONT = pg.sysfont.SysFont("console", 16)

WIN = pg.display.set_mode((1000, 1000))

while 1:
    for e in pg.event.get():
        if e.type == pg.QUIT:
            pg.quit()
            exit()

    WIN.fill("white")
    pg.draw.lines(WIN, "black",  True,  TRACK_POINTS,   3)
    pg.draw.lines(WIN, "gray10", False, PITLANE_POINTS, 2)


    for n, p in enumerate(PITLANE_POINTS):
        if "speed-limit-start" in PITLANE[n][2] or "speed-limit-end" in PITLANE[n][2]:
            pg.draw.circle(WIN, "yellow",  (p[0], p[1]), 6)

        if "pit-box" in PITLANE[n][2]:
            pg.draw.circle(WIN, "pink", (p[0], p[1]), 6)

        pg.draw.circle(WIN, "darkred", (p[0], p[1]), 2)
        # WIN.blit(FONT.render(str(n), False, "darkred"), (p[0], p[1]))


    for n, p in enumerate(TRACK_POINTS):
        if "turn-end" in TRACK[n][2]:
            pg.draw.circle(WIN, "red",  (p[0], p[1]), 8)

        if "turn-start" in TRACK[n][2]:
            pg.draw.circle(WIN, "lime", (p[0], p[1]), 6)

        pg.draw.circle(WIN, "darkred", (p[0], p[1]), 2)
        WIN.blit(FONT.render(str(n), False, "darkred"), (p[0], p[1]))

    pg.display.flip()