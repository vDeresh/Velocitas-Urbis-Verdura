import sys
import json
from os import path


def show():
    with open(path.abspath(path.join("src", "data", "tracks", sys.argv[1])), "r") as file:
        return json.load(file)[sys.argv[2]]


# TRACK = show()['track']
# TRACK_POINTS = []
# for x, y, *_ in TRACK:
#     TRACK_POINTS.append((x, y))


class Point:
    def __init__(self, x: int, y: int, c1: tuple[int, int], c2: tuple[int, int], tags: list) -> None:
        self.x: int = x
        self.y: int = y
        self.cx1: int = c1[0]
        self.cy1: int = c1[1]
        self.cx2: int = c2[0]
        self.cy2: int = c2[1]

        self.tags: list = tags



def compute_bezier_points(vertices, numPoints):
    if numPoints < 2 or len(vertices) != 4:
        raise ValueError("Line 26")

    result = []

    b0x = vertices[0][0]
    b0y = vertices[0][1]
    b1x = vertices[1][0]
    b1y = vertices[1][1]
    b2x = vertices[2][0]
    b2y = vertices[2][1]
    b3x = vertices[3][0]
    b3y = vertices[3][1]



    # Compute polynomial coefficients from Bezier points
    ax = -b0x + 3 * b1x + -3 * b2x + b3x
    ay = -b0y + 3 * b1y + -3 * b2y + b3y

    bx = 3 * b0x + -6 * b1x + 3 * b2x
    by = 3 * b0y + -6 * b1y + 3 * b2y

    cx = -3 * b0x + 3 * b1x
    cy = -3 * b0y + 3 * b1y

    dx = b0x
    dy = b0y

    # Set up the number of steps and step size
    numSteps = numPoints - 1 # arbitrary choice
    h = 1.0 / numSteps # compute our step size

    # Compute forward differences from Bezier points and "h"
    pointX = dx
    pointY = dy

    firstFDX = ax * (h * h * h) + bx * (h * h) + cx * h
    firstFDY = ay * (h * h * h) + by * (h * h) + cy * h


    secondFDX = 6 * ax * (h * h * h) + 2 * bx * (h * h)
    secondFDY = 6 * ay * (h * h * h) + 2 * by * (h * h)

    thirdFDX = 6 * ax * (h * h * h)
    thirdFDY = 6 * ay * (h * h * h)

    # Compute points at each step
    result.append((int(pointX), int(pointY)))

    for _ in range(numSteps):
        pointX += firstFDX
        pointY += firstFDY

        firstFDX += secondFDX
        firstFDY += secondFDY

        secondFDX += thirdFDX
        secondFDY += thirdFDY

        result.append((int(pointX), int(pointY)))

    return result


TRACK_TURN_POINTS: list[Point] = []
TRACK: list[list] = []
TRACK_POINTS: list[tuple[int, int]] = []


        # print()
        # for n, p in enumerate(fin_points):
        #     if n == 1:
        #         print(f"            [{p[0]}, {p[1]}, " + '["turn-start", {"reference-target-speed": 0, "overtaking-risk": 0.0}]],')
        #     elif n == len(fin_points) - 1:
        #         print(f"            [{p[0]}, {p[1]}, " + '["turn-end"]],')
        #     else:
        #         print(f"            [{p[0]}, {p[1]}, " + '[]],')
        # print()



def calculate_track_points():
    TRACK.clear()
    for n in range(len(TRACK_TURN_POINTS) - 1):
        point1 = TRACK_TURN_POINTS[n]
        point2 = TRACK_TURN_POINTS[n + 1]

        control_points = [(point1.x, point1.y), (point1.cx1, point1.cy1), (point2.cx2, point2.cy2), (point2.x, point2.y)]
        for x, y in compute_bezier_points(control_points, 16):
            TRACK.append([x, y, TRACK_TURN_POINTS[n].tags])

    TRACK_POINTS.clear()
    for p in TRACK:
        TRACK_POINTS.append(tuple(p[0:2]))


import pygame as pg

WIN = pg.display.set_mode((1000, 1000), pg.SCALED)


temp_mouse_down_point: None | tuple[int, int] = None
temp_mouse_down_info:  None | list            = None

_current_surface_type = "asphalt"

while 1:
    MOUSE_POS = pg.mouse.get_pos()
    MOUSE_PRESSED = pg.mouse.get_pressed()


    for e in pg.event.get():
        if e.type == pg.QUIT:
            pg.quit()

        if e.type == pg.KEYDOWN:
            if e.key == pg.K_s:
                file_name = input("Track name > ")
                author_name = input("Author(s) > ")
                allowed_racing_types = input("Allowed racing types > ") # TODO do not json.dump as in will delete previous tracks in the circuit

                with open(path.abspath(path.join("src", "data", "tracks", file_name)), "r") as file:
                    json.load(file)
                    json.dump(
                        {
                            "allowed-racing-types": ["formula"], # TODO
                        },
                        file
                    )

        if e.type == pg.MOUSEBUTTONDOWN:
            if e.button == 1:
                temp_mouse_down_point = e.pos
                temp_mouse_down_info = ["asphalt"]
            elif e.button == 3:
                temp_mouse_down_point = e.pos
                temp_mouse_down_info = ["dirt"]

        if e.type == pg.MOUSEBUTTONUP:
            if temp_mouse_down_point and temp_mouse_down_info:
                if e.button in [1, 3]:
                    TRACK_TURN_POINTS.append(Point(temp_mouse_down_point[0], temp_mouse_down_point[1], MOUSE_POS, (temp_mouse_down_point[0] + (temp_mouse_down_point[0] - MOUSE_POS[0]), temp_mouse_down_point[1] + (temp_mouse_down_point[1] - MOUSE_POS[1])), temp_mouse_down_info))
                    calculate_track_points()
                    temp_mouse_down_point = None
                    temp_mouse_down_info = None


    WIN.fill("white")

    if temp_mouse_down_point:
        pg.draw.line(WIN, "red", temp_mouse_down_point, MOUSE_POS)
        pg.draw.line(WIN, "red", temp_mouse_down_point, (temp_mouse_down_point[0] + (temp_mouse_down_point[0] - MOUSE_POS[0]), temp_mouse_down_point[1] + (temp_mouse_down_point[1] - MOUSE_POS[1])))
        pg.draw.circle(WIN, "orange", temp_mouse_down_point, 2)


    if len(TRACK_POINTS):
        # pg.draw.lines(WIN, "black", True, TRACK_POINTS) # type: ignore
        for n, p in enumerate(TRACK):
            if "asphalt" in p[2]: _current_surface_type = "asphalt"
            elif "dirt" in p[2]: _current_surface_type = "dirt"

            if _current_surface_type == "asphalt":
                if n != len(TRACK_POINTS) - 1:
                    pg.draw.line(WIN, "black", TRACK_POINTS[n], TRACK_POINTS[n + 1])
                else:
                    pg.draw.line(WIN, "black", TRACK_POINTS[n], TRACK_POINTS[0])

            elif _current_surface_type == "dirt":
                if n != len(TRACK_POINTS) - 1:
                    pg.draw.line(WIN, "orange", TRACK_POINTS[n], TRACK_POINTS[n + 1])
                else:
                    pg.draw.line(WIN, "orange", TRACK_POINTS[n], TRACK_POINTS[0])

        for p in TRACK_POINTS:
            pg.draw.circle(WIN, "darkred", p[0 : 2], 2)

    for p in TRACK_TURN_POINTS:
        pg.draw.circle(WIN, "aqua", (p.x, p.y), 4)

    pg.display.flip()