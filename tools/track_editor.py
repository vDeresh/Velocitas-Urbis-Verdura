import pygame as pg

import curses.textpad
import sys
import json
from os import path

from threading import Thread
import curses, _curses


SETTINGS = {
    'bezier-num-of-points': 16,
    'timer-tag-frequency': 10,
    'grid-size': 0
}


def round_half_up(n) -> int:
    if n - int(n) < 0.5:
        return int(n)
    else:
        return int(n) + 1


def snap_point_to_grid(point: tuple[int, int]) -> tuple[int, int]:
    if SETTINGS['grid-size']:
        return round_half_up(point[0] / SETTINGS['grid-size']) * SETTINGS['grid-size'], round_half_up(point[1] / SETTINGS['grid-size']) * SETTINGS['grid-size']
    return point

def snap_n_to_grid(n: int) -> int:
    if SETTINGS['grid-size']:
        return round_half_up(n / SETTINGS['grid-size']) * SETTINGS['grid-size']
    return n


def closest_point(to: tuple[int, int]) -> None | int:
    min_d = float("inf")
    point = 0

    for n, p in enumerate(TRACK_TURN_POINTS):
        d = pg.Vector2(to).distance_to(p.xy)
        if d < min_d:
            min_d = d
            point = n

    if min_d < 8:
        return point
    else:
        return None

def closest_checkpoint(to: tuple[int, int]) -> None | tuple[int, int]:
    min_d = float("inf")
    point = 0
    checkpoint = 0

    for n, p in enumerate(TRACK_TURN_POINTS):
        d = pg.Vector2(to).distance_to((p.cx0, p.cy0))
        if d < min_d:
            min_d = d
            point = n
            checkpoint = 0

    for n, p in enumerate(TRACK_TURN_POINTS):
        d = pg.Vector2(to).distance_to((p.cx1, p.cy1))
        if d < min_d:
            min_d = d
            point = n
            checkpoint = 1

    if min_d < 8:
        return (point, checkpoint)
    else:
        return None


def show():
    with open(path.abspath(path.join("src", "data", "tracks", sys.argv[1])), "r") as file:
        return json.load(file)[sys.argv[2]]


class Point:
    def __init__(self, xy: tuple[int, int], c0: tuple[int, int], c1: tuple[int, int], tags: list) -> None:
        self.x: int = xy[0]
        self.y: int = xy[1]
        self.cx0: int = c0[0]
        self.cy0: int = c0[1]
        self.cx1: int = c1[0]
        self.cy1: int = c1[1]
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

        control_points = [(point1.x, point1.y), (point1.cx0, point1.cy0), (point2.cx1, point2.cy1), (point2.x, point2.y)]

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
    if not len(TRACK):
        return

    for n, p in enumerate(TRACK):
        if "timer" in p[2]:
            if "asphalt" in TRACK[n][2]:
                TRACK[n][2].clear()
                TRACK[n][2].append("asphalt")

            elif "dirt" in TRACK[n][2]:
                TRACK[n][2].clear()
                TRACK[n][2].append("dirt")

            else:
                TRACK[n][2].clear()

    TRACK[0][2].insert(0, "meta")
    for n, p in enumerate(TRACK):
        if (not n % SETTINGS['timer-tag-frequency']) or ("drs-start" in p[2]) or ("drs-end" in p[2]):
            TRACK[n][2].insert(0, "timer")



def terminal(stdscr: _curses.window) -> None:
    curses.curs_set(0)
    stdscr.nodelay(True)

    textbox_win = curses.newwin(1, 115, 12, 5)
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


        curses.textpad.rectangle(stdscr, 6, 1, 10, 44)
        stdscr.addstr(6, 2, " Editor info ")
        stdscr.addstr(7, 3, f"bnop:                {SETTINGS['bezier-num-of-points']}")
        stdscr.addstr(8, 3, f"timer tag frequency: {SETTINGS['timer-tag-frequency']}")
        stdscr.addstr(9, 3, f"grid size:           {SETTINGS['grid-size']}")


        curses.textpad.rectangle(stdscr, 1, 45, 10, 120)
        stdscr.addstr(1, 46, " Help ")
        stdscr.addstr(2, 47, "update")

        stdscr.addstr(3, 47, "bnop") # <n>
        stdscr.addstr(3, 52, "<n>")
        stdscr.addstr(3, 56, "sets amount of points in curves to n (default: 16)", curses.A_REVERSE)

        stdscr.addstr(4, 47, "save") # <track name> <racing type> <author(s)>
        stdscr.addstr(4, 52, "<track name>")
        stdscr.addstr(4, 65, "<racing type>")
        stdscr.addstr(4, 79, "[*author(s)]")
        stdscr.addstr(4, 91, "saves track (one racing type)", curses.A_REVERSE)

        stdscr.addstr(5, 47, "tag") # <*frequency>
        stdscr.addstr(5, 51, "<*frequency>")
        stdscr.addstr(5, 64, "auto-tags track", curses.A_REVERSE)

        stdscr.addstr(6, 47, "grid") # <size>
        stdscr.addstr(6, 52, "<size>") # <size>
        stdscr.addstr(6, 59, "sets size of the grid (default: 0)", curses.A_REVERSE) # <size>


        curses.textpad.rectangle(stdscr, 11, 1, 13, 120)
        stdscr.addstr(11, 2, " Command line ")
        stdscr.addstr(12, 3, ">")

        curses.textpad.rectangle(stdscr, 14, 1, 16, 120)
        stdscr.addstr(14, 2, " Latest error ")
        stdscr.addstr(15, 3, TERMINAL_ERROR_MESSAGE)

        stdscr.refresh()

        try:
            if stdscr.getkey() == "\n":
                curses.curs_set(1)

                textbox.edit()
                command = textbox.gather().split()

                match command[0]:
                    case "bnop": # <n>
                        if len(command) == 2:
                            if command[1].isdigit():
                                if int(command[1]) > 1:
                                    SETTINGS.update({'bezier-num-of-points': int(command[1])})
                                else:
                                    TERMINAL_ERROR_MESSAGE = f"parameter in `bnop` command must be a number bigger than 1 ('{command[1]}' provided)"
                            else:
                                TERMINAL_ERROR_MESSAGE = f"parameter in `bnop` command must be a number bigger than 1 ('{command[1]}' provided)"
                        else:
                            TERMINAL_ERROR_MESSAGE = f"`bnop` command takes 1 parameter ({len(command) - 1} provided)"

                    case "tag": # <*frequency>
                        if len(command) == 2:
                            if command[1].isdigit() and int(command[1]) > 1:
                                SETTINGS.update({'timer-tag-frequency': int(command[1])})
                            else:
                                TERMINAL_ERROR_MESSAGE = f"`tag` command parameter must be a number bigger than 1 ('{command[1]}' provided)"
                        elif len(command) > 2:
                            TERMINAL_ERROR_MESSAGE = f"`tag` command takes 1 (optional) parameter ({len(command) - 1} provided)"
                        tag_track()

                    case "grid": # <size>
                        if len(command) == 2:
                            if command[1].isdigit() and int(command[1]) >= 0:
                                SETTINGS.update({'grid-size': int(command[1])})
                            else:
                                TERMINAL_ERROR_MESSAGE = f"`grid` command parameter must be a positive number ('{command[1]}' provided)"
                        else:
                            TERMINAL_ERROR_MESSAGE = f"`grid` command takes 1 parameter ({len(command) - 1} provided)"

                    case "snap": # <*grid-size>
                        if len(command) == 1:
                            for n, p in enumerate(TRACK_TURN_POINTS):
                                TRACK_TURN_POINTS[n].x, TRACK_TURN_POINTS[n].y = snap_point_to_grid(p.xy)
                        elif len(command) == 2:
                            for n, p in enumerate(TRACK_TURN_POINTS):
                                TRACK_TURN_POINTS[n].x, TRACK_TURN_POINTS[n].y = snap_point_to_grid(p.xy)
                        else:
                            TERMINAL_ERROR_MESSAGE = f"`snap` command takes 1 (optional) parameter ({len(command) - 1} provided)"

                    case "update":
                        if len(command) == 1:
                            calculate_track_points()
                        else:
                            TERMINAL_ERROR_MESSAGE = f"`update` command takes no parameters"

                    case "save": # <track name> <racing type> [*author(s)]
                        if len(command) < 2 + 1:
                            TERMINAL_ERROR_MESSAGE = f"`save` command takes atleast 2 parameters ({len(command) - 1} provided)"
                            continue
                        if not command[2] in ["formula", "rallycross"]:
                            TERMINAL_ERROR_MESSAGE = f"<racing type> parameter in `save` command must be 'formula' or 'rallycross' ('{command[2]}' provided)"
                            continue

                        path_to_file = path.abspath(path.join("src", "data", "tracks", command[1]))

                        while 1:
                            try:
                                with open(path_to_file, "r") as file:
                                    final_file: dict = json.load(file)

                                    if not command[2] in final_file['allowed-racing-types']:
                                        final_file['allowed-racing-types'].append(command[2])

                                    if len(command) < 3 + 1:
                                        for n in range(3, len(command)):
                                            if command[n] not in final_file['authors']:
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
                                    json.dump(final_file, file, indent=None)

                                with open(path_to_file, "r+") as file:
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

                    case _other:
                        TERMINAL_ERROR_MESSAGE = f"command `{_other}` does not exist"
                        del _other

        except _curses.error: pass
        finally:
            textbox_win.clear()
            curses.curs_set(0)


# _thread_terminal = Thread(target=curses.wrapper, args=[terminal], name="thread-terminal", daemon=True)
# _thread_terminal.start()



WIN = pg.display.set_mode((1000, 1000), pg.SCALED)


temp_mouse_down_point: None | tuple[int, int] = None
temp_mouse_down_info:  None | list            = None

temp_selected_point:      None | int = None
temp_selected_checkpoint: None | tuple[int, int] = None

_current_surface_type = "asphalt"

while 1:
    MOUSE_POS     = pg.mouse.get_pos()
    MOUSE_PRESSED = pg.mouse.get_pressed()
    KEY_PRESSED   = pg.key.get_pressed()

    for e in pg.event.get():
        if e.type == pg.QUIT:
            pg.quit()
            exit()

        if e.type == pg.MOUSEMOTION:
            if KEY_PRESSED[pg.K_LALT]:
                if temp_selected_checkpoint:
                    exec(
                        f"TRACK_TURN_POINTS[temp_selected_checkpoint[0]].cx{temp_selected_checkpoint[1]} += e.rel[0];"
                        f"TRACK_TURN_POINTS[temp_selected_checkpoint[0]].cy{temp_selected_checkpoint[1]} += e.rel[1]"
                    )
                    calculate_track_points()

        if e.type == pg.MOUSEBUTTONDOWN:
            if temp_mouse_down_info and temp_mouse_down_point:
                continue

            if KEY_PRESSED[pg.K_LSHIFT]:
                temp_selected_point = closest_point(MOUSE_POS)

            elif KEY_PRESSED[pg.K_LCTRL]:
                temp_selected_checkpoint = closest_checkpoint(MOUSE_POS)

            else:
                if e.button == 1:
                    temp_mouse_down_info = ["asphalt"]
                    temp_mouse_down_point = snap_point_to_grid(e.pos)

                elif e.button == 3:
                    temp_mouse_down_info = ["dirt"]
                    temp_mouse_down_point = snap_point_to_grid(e.pos)

        if e.type == pg.MOUSEBUTTONUP:
            print(e.button, temp_mouse_down_info)
            if temp_mouse_down_info
            if ((e.button == 1) and ("asphalt" in temp_mouse_down_info)) or ((e.button == 3) and ("dirt" in temp_mouse_down_info)):
                print(temp_mouse_down_point, temp_mouse_down_info)
                if temp_mouse_down_point and temp_mouse_down_info:
                    TRACK_TURN_POINTS.append(Point(temp_mouse_down_point, snap_point_to_grid(MOUSE_POS), snap_point_to_grid((temp_mouse_down_point[0] + (temp_mouse_down_point[0] - snap_n_to_grid(MOUSE_POS[0])), temp_mouse_down_point[1] + (temp_mouse_down_point[1] - snap_n_to_grid(MOUSE_POS[1])))), temp_mouse_down_info))
                    calculate_track_points()
                temp_selected_point = temp_selected_checkpoint = temp_mouse_down_point = temp_mouse_down_info = None


    WIN.fill("white")


    if SETTINGS['grid-size']:
        for n in range(SETTINGS['grid-size'], 1000 - SETTINGS['grid-size'] + 1, SETTINGS['grid-size']):
            pg.draw.line(WIN, "gray80", (n, 0), (n, 1000))
            pg.draw.line(WIN, "gray80", (0, n), (1000, n))


    if temp_selected_point:
        TRACK_TURN_POINTS[temp_selected_point].cx0, TRACK_TURN_POINTS[temp_selected_point].cy0 = TRACK_TURN_POINTS[temp_selected_point].cx0 - (TRACK_TURN_POINTS[temp_selected_point].x - MOUSE_POS[0]), TRACK_TURN_POINTS[temp_selected_point].cy0 - (TRACK_TURN_POINTS[temp_selected_point].y - MOUSE_POS[1])
        TRACK_TURN_POINTS[temp_selected_point].cx1, TRACK_TURN_POINTS[temp_selected_point].cy1 = TRACK_TURN_POINTS[temp_selected_point].cx1 - (TRACK_TURN_POINTS[temp_selected_point].x - MOUSE_POS[0]), TRACK_TURN_POINTS[temp_selected_point].cy1 - (TRACK_TURN_POINTS[temp_selected_point].y - MOUSE_POS[1])
        TRACK_TURN_POINTS[temp_selected_point].x,   TRACK_TURN_POINTS[temp_selected_point].y   = MOUSE_POS

        TRACK_TURN_POINTS[temp_selected_point].x,   TRACK_TURN_POINTS[temp_selected_point].y   = snap_point_to_grid(TRACK_TURN_POINTS[temp_selected_point].xy)
        TRACK_TURN_POINTS[temp_selected_point].cx0, TRACK_TURN_POINTS[temp_selected_point].cy0 = snap_point_to_grid((TRACK_TURN_POINTS[temp_selected_point].cx0, TRACK_TURN_POINTS[temp_selected_point].cy0))
        TRACK_TURN_POINTS[temp_selected_point].cx1, TRACK_TURN_POINTS[temp_selected_point].cy1 = snap_point_to_grid((TRACK_TURN_POINTS[temp_selected_point].cx1, TRACK_TURN_POINTS[temp_selected_point].cy1))

        calculate_track_points()


    if temp_selected_checkpoint:
        exec(
            f"TRACK_TURN_POINTS[temp_selected_checkpoint[0]].cx{temp_selected_checkpoint[1]}, TRACK_TURN_POINTS[temp_selected_checkpoint[0]].cy{temp_selected_checkpoint[1]} = MOUSE_POS;"
            f"TRACK_TURN_POINTS[temp_selected_checkpoint[0]].cx{temp_selected_checkpoint[1]}, TRACK_TURN_POINTS[temp_selected_checkpoint[0]].cy{temp_selected_checkpoint[1]} = snap_point_to_grid((TRACK_TURN_POINTS[temp_selected_checkpoint[0]].cx{temp_selected_checkpoint[1]}, TRACK_TURN_POINTS[temp_selected_checkpoint[0]].cy{temp_selected_checkpoint[1]}));"
        )

        calculate_track_points()


    if temp_mouse_down_point and temp_mouse_down_info:
        _temp_checkpoint_0 = snap_point_to_grid(MOUSE_POS)
        _temp_checkpoint_1 = snap_point_to_grid((temp_mouse_down_point[0] + (temp_mouse_down_point[0] - snap_n_to_grid(MOUSE_POS[0])), temp_mouse_down_point[1] + (temp_mouse_down_point[1] - snap_n_to_grid(MOUSE_POS[1]))))

        TRACK_TURN_POINTS.append(Point(temp_mouse_down_point, _temp_checkpoint_0, _temp_checkpoint_1, temp_mouse_down_info))
        calculate_track_points()

        pg.draw.line(WIN, "red", temp_mouse_down_point, _temp_checkpoint_0)
        pg.draw.line(WIN, "red", temp_mouse_down_point, _temp_checkpoint_1)

        pg.draw.circle(WIN, "red", _temp_checkpoint_0, 4)
        pg.draw.circle(WIN, "red", _temp_checkpoint_1, 4)

        if "asphalt" in temp_mouse_down_info:
            pg.draw.circle(WIN, "aqua", temp_mouse_down_point, 2)
        elif "dirt" in temp_mouse_down_info:
            pg.draw.circle(WIN, "orange", temp_mouse_down_point, 2)


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
            pg.draw.circle(WIN, "aqua", p.xy, 6)
        elif "dirt" in p.tags:
            pg.draw.circle(WIN, "orange", p.xy, 6)

    for p in TRACK:
        if "timer" in p[2]:
            pg.draw.circle(WIN, "yellow", p[0:2], 4)
        pg.draw.circle(WIN, "darkred", p[0:2], 2)


    if KEY_PRESSED[pg.K_LCTRL]:
        for p in TRACK_TURN_POINTS:
            pg.draw.line(WIN, "green", p.xy, (p.cx0, p.cy0))
            pg.draw.line(WIN, "green", p.xy, (p.cx1, p.cy1))
            pg.draw.circle(WIN, "lime", (p.cx0, p.cy0), 6)
            pg.draw.circle(WIN, "lime", (p.cx1, p.cy1), 6)


    pg.display.flip()

    if temp_mouse_down_point:
        TRACK_TURN_POINTS.pop()