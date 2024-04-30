import sys
from pygame import Vector2


class Point:
    def __init__(self, x: int, y: int, cx: int, cy: int) -> None:
        self.x:  int = x
        self.y:  int = y
        self.cx: int = cx
        self.cy: int = cy


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

if len(sys.argv) == 8 + 1:
    p1 = Point(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]))
    p2 = Point(int(sys.argv[5]), int(sys.argv[6]), int(sys.argv[7]), int(sys.argv[8]))

    control_points = [(int(sys.argv[1]), int(sys.argv[2])), (int(sys.argv[3]), int(sys.argv[4])), (int(sys.argv[7]), int(sys.argv[8])), (int(sys.argv[5]), int(sys.argv[6]))]
    fin_points = compute_bezier_points(control_points, 16)
    print()
    for n, p in enumerate(fin_points):
        if n == 0:
            print(f"            [{p[0]}, {p[1]}, " + '["turn-start", {"reference-target-speed": 70, "overtaking-risk": 0.7}]],')
        elif n == len(fin_points) - 1:
            print(f"            [{p[0]}, {p[1]}, " + '["turn-end"]],')
        else:
            print(f"            [{p[0]}, {p[1]}, " + '[]],')
    print()

elif len(sys.argv) == 4 + 1:
    p1 = Vector2(int(sys.argv[1]), int(sys.argv[2]))
    p2 = Vector2(int(sys.argv[3]), int(sys.argv[4]))

    straight_lenght = p1.distance_to(p2)
    segment_length = int(straight_lenght / 16)
    direction = Vector2(p1.x - p2.x, p1.y - p2.y).normalize()

    fin_points = []
    for n in range(16):
        new_point = p1 - n * segment_length * direction
        fin_points.append((int(new_point.x), int(new_point.y)))

    print()
    for n, p in enumerate(fin_points):
        if n == 0:
            print(f"            [{p[0]}, {p[1]}, " + '["straight-start", {"length":', str(straight_lenght) + ', "overtaking-risk": 0.7}]],')
        elif n == len(fin_points) - 1:
            print(f"            [{p[0]}, {p[1]}, " + '["straight-end"]],')
        else:
            print(f"            [{p[0]}, {p[1]}, " + '[]],')
    print()

import pygame as pg

WIN = pg.display.set_mode((1000, 1000))

while 1:
    for e in pg.event.get():
        if e.type == pg.QUIT:
            pg.quit()
            sys.exit()

    WIN.fill("white")
    pg.draw.lines(WIN, "black", False, fin_points, 3)

    for p in fin_points:
        pg.draw.circle(WIN, "red", p, 2)

    pg.display.flip()