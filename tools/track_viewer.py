import sys
import json
from os import path


# def show():
#     with open(path.abspath(path.join("src", "data", "racing-categories", sys.argv[1], "tracks")), "r") as file:
#         return json.load(file)

def show():
    with open(path.abspath(path.join("src", "data", "tracks", sys.argv[1])), "r") as file:
        return json.load(file)[sys.argv[2]]


TRACK = show()['track']
TRACK_POINTS = []
for x, y, *_ in TRACK:
    TRACK_POINTS.append((x, y))

if sys.argv[2] != 'rallycross':
    PITLANE = show()['pit-lane']
    PITLANE_POINTS = []
    for x, y, *_ in PITLANE:
        PITLANE_POINTS.append((x, y))

    drs_zone = []
    for n, p in enumerate(TRACK):
        if "drs-start" in p[2]:
            for p2 in TRACK[n:] + TRACK[:n]:
                drs_zone.append(p2[0 : 2])
                if "drs-end" in p2[2]:
                    break


import pygame as pg

pg.font.init()
FONT = pg.sysfont.SysFont("console", 12)

WIN = pg.display.set_mode((1000, 1000))

if sys.argv[2] != 'rallycross':
    while 1:
        for e in pg.event.get():
            if e.type == pg.QUIT:
                pg.quit()
                exit()

        WIN.fill("white")
        pg.draw.lines(WIN, "black",  True,  TRACK_POINTS,   1)

        if len(PITLANE_POINTS):
            pg.draw.lines(WIN, "gray10", False, PITLANE_POINTS, 1)

        for n, p in enumerate(PITLANE_POINTS):
            if "speed-limit-start" in PITLANE[n][2] or "speed-limit-end" in PITLANE[n][2]:
                pg.draw.circle(WIN, "yellow",  (p[0], p[1]), 6)

            if "pit-box" in PITLANE[n][2]:
                pg.draw.circle(WIN, "pink", (p[0], p[1]), 6)

            pg.draw.circle(WIN, "darkred", (p[0], p[1]), 2)
            # WIN.blit(FONT.render(str(n), False, "darkred"), (p[0], p[1]))


        for n, p in enumerate(TRACK_POINTS):
            if "turn-end" in TRACK[n][2]:
                pg.draw.circle(WIN, "red",  (p[0], p[1]), 6)

            if "turn-start" in TRACK[n][2]:
                pg.draw.circle(WIN, "lime", (p[0], p[1]), 5)
                WIN.blit(FONT.render(str(p), False, "darkred"), (p[0], p[1]))

            if "timer" in TRACK[n][2]:
                pg.draw.circle(WIN, "orange", (p[0], p[1]), 4)

            if "braking-finish-point" in TRACK[n][2]:
                pg.draw.circle(WIN, "pink", (p[0], p[1]), 4)

            if "acceleration-start-point" in TRACK[n][2]:
                pg.draw.circle(WIN, "green", (p[0], p[1]), 4)

            pg.draw.circle(WIN, "darkred", (p[0], p[1]), 2)
            # WIN.blit(FONT.render(str(n), False, "darkred"), (p[0], p[1]))

        if len(drs_zone):
            pg.draw.lines(WIN, "lime", False, drs_zone, 2)

        pg.display.flip()

else:
    while 1:
        for e in pg.event.get():
            if e.type == pg.QUIT:
                pg.quit()
                exit()

        WIN.fill("white")
        pg.draw.lines(WIN, "black",  True,  TRACK_POINTS,   1)

        for n, p in enumerate(TRACK_POINTS):
            if "turn-end" in TRACK[n][2]:
                pg.draw.circle(WIN, "red",  (p[0], p[1]), 6)
            if "turn-start" in TRACK[n][2]:
                pg.draw.circle(WIN, "lime", (p[0], p[1]), 6)
                WIN.blit(FONT.render(str(p), False, "darkred"), (p[0], p[1]))

            if "braking-finish-point" in TRACK[n][2]:
                pg.draw.circle(WIN, "pink", (p[0], p[1]), 5)
            if "acceleration-start-point" in TRACK[n][2]:
                pg.draw.circle(WIN, "green", (p[0], p[1]), 5)

            if "timer" in TRACK[n][2]:
                pg.draw.circle(WIN, "orange", (p[0], p[1]), 4)

            pg.draw.circle(WIN, "darkred", (p[0], p[1]), 2)
            # WIN.blit(FONT.render(str(n), False, "darkred"), (p[0], p[1]))

        pg.display.flip()