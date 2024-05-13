import curses.textpad
import sys
import json
from os import path

from threading import Thread
import curses, _curses


SETTINGS = {
    'bezier-num-of-points': 16,
    'timer-tag-frequency': 10
}


def show():
    with open(path.abspath(path.join("src", "data", "tracks", sys.argv[1])), "r") as file:
        return json.load(file)[sys.argv[2]]


class Point:
    def __init__(self, x: int, y: int, c1: tuple[int, int], c2: tuple[int, int], tags: list) -> None:
        self.x: int = x
        self.y: int = y
        self.cx1: int = c1[0]
        self.cy1: int = c1[1]
        self.cx2: int = c2[0]
        self.cy2: int = c2[1]

        self.tags: list = tags

    @property
    def xy(self) -> tuple[int, int]:
        return self.x, self.y


def compute_bezier_points(vertices) -> list[tuple[int, int]]:
    numPoints = SETTINGS['bezier-num-of-points']

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


def is_similar(p1, p2, _range: int = 2) -> bool:
    for n in range(-_range, _range):
        if p1[0] + n == p2[0]:
            break
    else:
        return False

    for n in range(-_range, _range):
        if p1[1] + n == p2[1]:
            break
    else:
        return False

    return True


def calculate_track_points():
    if len(TRACK_TURN_POINTS) < 2:
        return

    TRACK.clear()
    for n in range(len(TRACK_TURN_POINTS) - 1):
        point1 = TRACK_TURN_POINTS[n]
        point2 = TRACK_TURN_POINTS[n + 1]

        control_points = [(point1.x, point1.y), (point1.cx1, point1.cy1), (point2.cx2, point2.cy2), (point2.x, point2.y)]

        for x, y in compute_bezier_points(control_points):
            TRACK.append([x, y, point1.tags])

    TRACK_POINTS.clear()
    temp_TRACK = []
    for n, p in enumerate(TRACK):
        if (n == 0) or (not is_similar(p[0:2], TRACK[n - 1][0:2])): # (p != TRACK_POINTS[n - 1]):
            TRACK_POINTS.append(tuple(p[0:2]))

            if n == 0:
                temp_TRACK.append([p[0], p[1], p[2] + ["timer", "meta"]])
            else:
                temp_TRACK.append(p)
    else:
        TRACK.clear()
        TRACK.extend(temp_TRACK)

    temp_TRACK = []
    _temp_current_surface_type = ""
    for n, p in enumerate(TRACK):
        if (n > 0) and (_temp_current_surface_type in p[2]):
            temp_p2 = p[2].copy()
            temp_p2.remove(_temp_current_surface_type)
            temp_TRACK.append([p[0], p[1], temp_p2])
        else:
            temp_TRACK.append(p)

        if "asphalt" in p[2]: _temp_current_surface_type = "asphalt"
        elif "dirt" in p[2]: _temp_current_surface_type = "dirt"
    else:
        TRACK.clear()
        TRACK.extend(temp_TRACK)

    temp_TRACK = []
    for n, p in enumerate(TRACK[:len(TRACK) - 1]):
        temp_p2 = p[2]

        if "asphalt" in TRACK[n + 1][2]:
            temp_p2.insert(0, "asphalt")
        elif "dirt" in TRACK[n + 1][2]:
            temp_p2.insert(0, "dirt")

        temp_TRACK.append([p[0], p[1], temp_p2])
    else:
        temp_TRACK.append(TRACK[-1])
        TRACK.clear()
        TRACK.extend(temp_TRACK)


def tag_track():
    for n, p in enumerate(TRACK):
        if "timer" in p[2]:
            TRACK[n][2].remove("timer")

    for n, p in enumerate(TRACK):
        if (not n % SETTINGS['timer-tag-frequency']) or ("drs-start" in p[2]) or ("drs-end" in p[2]):
            TRACK[n][2].insert(0, "timer")


import pygame as pg

WIN = pg.display.set_mode((1000, 1000), pg.SCALED)


temp_mouse_down_point: None | tuple[int, int] = None
temp_mouse_down_info:  None | list            = None

_current_surface_type = "asphalt"


def terminal(stdscr: _curses.window) -> None:
    curses.curs_set(0)
    # curses.start_color()
    stdscr.nodelay(True)

    # curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_CYAN)

    textbox_win = curses.newwin(1, 115, 11, 5)
    textbox = curses.textpad.Textbox(textbox_win)

    TERMINAL_ERROR_MESSAGE = ""

    while 1:
        stdscr.clear()

        curses.textpad.rectangle(stdscr, 1, 1, 5, 44)
        stdscr.addstr(1, 2, " Track info ")
        stdscr.addstr(2, 3, f"amount of points:   {len(TRACK_POINTS)}")
        stdscr.addstr(3, 3, f"track length:       {sum([pg.Vector2(TRACK_POINTS[n]).distance_to(TRACK_POINTS[n + 1]) for n in range(len(TRACK_POINTS) - 1)])}")

        if len(TRACK_POINTS) >= 3:
            stdscr.addstr(4, 3, f"starting direction: {pg.Vector2(TRACK_POINTS[0][0] - TRACK_POINTS[-1][0], TRACK_POINTS[0][1] - TRACK_POINTS[-1][1]).normalize()}")
        else:
            stdscr.addstr(4, 3, f"starting direction: (not enough points)")


        curses.textpad.rectangle(stdscr, 6, 1, 9, 44)
        stdscr.addstr(6, 2, " Editor info ")
        stdscr.addstr(7, 3, f"bnop:                {SETTINGS['bezier-num-of-points']}")
        stdscr.addstr(8, 3, f"timer tag frequency: {SETTINGS['timer-tag-frequency']}")


        curses.textpad.rectangle(stdscr, 1, 45, 9, 120)
        stdscr.addstr(1, 46, " Help ")
        stdscr.addstr(2, 47, "update")

        stdscr.addstr(3, 47, "bnop") # <n>
        stdscr.addstr(3, 52, "<n>")
        stdscr.addstr(3, 56, "sets amount of points in curves to n (default: 16)", curses.A_REVERSE)

        stdscr.addstr(4, 47, "save") # <track name> <racing type> <author(s)>
        stdscr.addstr(4, 52, "<track name>")
        stdscr.addstr(4, 65, "<racing type>")
        stdscr.addstr(4, 79, "<author(s)>")
        stdscr.addstr(4, 91, "saves track (one racing type)", curses.A_REVERSE)

        stdscr.addstr(5, 47, "tag") # [frequency]
        stdscr.addstr(5, 51, "<*frequency>")
        stdscr.addstr(5, 64, "auto-tags track", curses.A_REVERSE)


        curses.textpad.rectangle(stdscr, 10, 1, 12, 120)
        stdscr.addstr(10, 2, " Command line ")
        stdscr.addstr(11, 3, ">")

        curses.textpad.rectangle(stdscr, 13, 1, 15, 120)
        stdscr.addstr(13, 2, " Latest error ")
        stdscr.addstr(14, 3, TERMINAL_ERROR_MESSAGE)

        stdscr.refresh()

        try:
            if stdscr.getkey() == "\n":
                curses.curs_set(1)

                textbox.edit()
                command = textbox.gather().split()

                match command[0]:
                    case "bnop": # <n>
                        if len(command) == 2:
                            if command[1].isalnum():
                                if int(command[1]) >= 2:
                                    SETTINGS.update({'bezier-num-of-points': int(command[1])})
                                else:
                                    TERMINAL_ERROR_MESSAGE = "`bnop` command parameter must be more than 1"
                            else:
                                TERMINAL_ERROR_MESSAGE = "parameter in `bnop` command must be alphanumeric"
                        else:
                            TERMINAL_ERROR_MESSAGE = f"`bnop` command takes 1 parameter ({len(command) - 1} provided)"

                    case "tag":
                        if len(command) > 1:
                            if command[1].isalnum() and int(command[1]) > 1:
                                SETTINGS.update({'timer-tag-frequency': int(command[1])})
                        tag_track()

                    case "update":
                        calculate_track_points()

                    case "save": # <track name> <racing type> <author(s)>
                        if len(command) < 4:
                            TERMINAL_ERROR_MESSAGE = f"`save` command takes atleast 3 parameters ({len(command) - 1} provided)"
                            continue
                        if (command[1].isalnum()) or (command[2].isalnum()) or (command[3].isalnum()):
                            TERMINAL_ERROR_MESSAGE = "all parameters in `save` command must be alphabetic strings"
                            continue

                        path_to_file = path.abspath(path.join("src", "data", "tracks", command[1]))

                        while 1:
                            try:
                                with open(path_to_file, "r") as file:
                                    final_file: dict = json.load(file)

                                    final_file['allowed-racing-types'].append(command[2])

                                    for n in range(3, len(command)):
                                        final_file['authors'].append(command[n])

                                    final_file.update({
                                        command[2]: {
                                            "features": {
                                                "pit-lane": 0,
                                                "drs": 0
                                            },

                                            "info": {
                                                "length": sum([pg.Vector2(TRACK_POINTS[n]).distance_to(TRACK_POINTS[n + 1]) for n in range(len(TRACK_POINTS) - 1)]),
                                                "starting-direction": list(pg.Vector2(TRACK_POINTS[0][0] - TRACK_POINTS[-1][0], TRACK_POINTS[0][1] - TRACK_POINTS[-1][1]).normalize()),

                                                "track-capacity": 0,
                                                "pit-lane-speed-limit": 0,
                                                "pit-lane-entry-point": 0,
                                                "pit-lane-exit-point": 0,

                                                "timer-ids": [],
                                                "timer-pos": []
                                            },

                                            "pit-lane": [],

                                            "track": TRACK
                                        }
                                    })

                                with open(path_to_file, "w") as file:
                                    json.dump(final_file, file)

                                with open("test.json", "r+") as file:
                                    content = file.read()
                                    content = content.replace("]], ", "]],\n").replace("\n", "\n    ")
                                    content = content.replace("[[", "[\n    [", 1)
                                    file.seek(0)
                                    file.write(content)
                                    file.truncate()

                                break

                            except (FileNotFoundError, json.decoder.JSONDecodeError):
                                with open(path_to_file, "w") as file:
                                    file.write("{}")

                                with open(path_to_file, "r") as file:
                                    json.load(file)

                                with open(path_to_file, "w") as file:
                                    json.dump({
                                        "allowed-racing-types": [],
                                        "authors": [],
                                        "via-editor": True,
                                    }, file)

        except _curses.error: pass
        finally:
            textbox_win.clear()
            curses.curs_set(0)


_thread_terminal = Thread(target=curses.wrapper, args=[terminal], name="thread-terminal", daemon=True)
_thread_terminal.start()


while 1:
    MOUSE_POS = pg.mouse.get_pos()
    MOUSE_PRESSED = pg.mouse.get_pressed()


    for e in pg.event.get():
        if e.type == pg.QUIT:
            pg.quit()
            exit()

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

    if temp_mouse_down_point and temp_mouse_down_info:
        TRACK_TURN_POINTS.append(Point(temp_mouse_down_point[0], temp_mouse_down_point[1], MOUSE_POS, (temp_mouse_down_point[0] + (temp_mouse_down_point[0] - MOUSE_POS[0]), temp_mouse_down_point[1] + (temp_mouse_down_point[1] - MOUSE_POS[1])), temp_mouse_down_info))
        calculate_track_points()

        pg.draw.line(WIN, "red", temp_mouse_down_point, MOUSE_POS)
        pg.draw.line(WIN, "red", temp_mouse_down_point, (temp_mouse_down_point[0] + (temp_mouse_down_point[0] - MOUSE_POS[0]), temp_mouse_down_point[1] + (temp_mouse_down_point[1] - MOUSE_POS[1])))

        if "asphalt" in temp_mouse_down_info:
            pg.draw.circle(WIN, "aqua", temp_mouse_down_point, 2)
        elif "dirt" in temp_mouse_down_info:
            pg.draw.circle(WIN, "orange", temp_mouse_down_point, 2)


    # if len(TRACK_POINTS):
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
                pg.draw.line(WIN, "orange2", TRACK_POINTS[n], TRACK_POINTS[n + 1])
            else:
                pg.draw.line(WIN, "orange2", TRACK_POINTS[n], TRACK_POINTS[0])

    for p in TRACK_TURN_POINTS:
        if "asphalt" in p.tags:
            pg.draw.circle(WIN, "aqua", p.xy, 4)
        elif "dirt" in p.tags:
            pg.draw.circle(WIN, "orange", p.xy, 4)

    for p in TRACK:
        if "timer" in p[2]:
            pg.draw.circle(WIN, "yellow", p[0:2], 4)
        pg.draw.circle(WIN, "darkred", p[0:2], 2)

    pg.display.flip()

    if temp_mouse_down_point:
        TRACK_TURN_POINTS.pop()