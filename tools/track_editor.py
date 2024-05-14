import pygame as pg

import curses.textpad
import sys
import json
from os import path

from threading import Thread
import curses, _curses


SETTINGS = {
    'EDITOR': {
        # 'global-bezier-num-of-points': 16,
        'current-bezier-num-of-points': 16,
        'timer-tag-frequency': 10,
        'grid-size': 0
    },

    'TRACK': {
        'scale': 1
    }
}


def round_half_up(n) -> int:
    if n - int(n) < 0.5:
        return int(n)
    else:
        return int(n) + 1


def snap_point_to_grid(point: tuple[int, int], grid_size: None | int = None) -> tuple[int, int]:
    if not grid_size:
        grid_size = SETTINGS['EDITOR']['grid-size']

    if grid_size:
        return round_half_up(point[0] / grid_size) * grid_size, round_half_up(point[1] / grid_size) * grid_size

    return point

def snap_n_to_grid(n: int) -> int:
    if SETTINGS['EDITOR']['grid-size']:
        return round_half_up(n / SETTINGS['EDITOR']['grid-size']) * SETTINGS['EDITOR']['grid-size']
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


class TurnPoint:
    def __init__(self, xy: tuple[int, int], c0: tuple[int, int], c1: tuple[int, int], tags: list, bnop: None | int = None) -> None:
        self.x: int = xy[0]
        self.y: int = xy[1]
        self.cx0: int = c0[0]
        self.cy0: int = c0[1]
        self.cx1: int = c1[0]
        self.cy1: int = c1[1]
        self.tags: list = tags
        self.index: int = len(TRACK) - 1

        if bnop:
            self.bnop: int = bnop
        else:
            self.bnop: int = SETTINGS['EDITOR']['current-bezier-num-of-points']


    @property
    def xy(self) -> tuple[int, int]:
        return self.x, self.y


def compute_bezier_points(vertices, numPoints: None | int = None) -> list[tuple[int, int]]:
    if not numPoints:
        # numPoints = SETTINGS['EDITOR']['global -bezier-num-of-points']
        numPoints = SETTINGS['EDITOR']['current-bezier-num-of-points']

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


TRACK_TURN_POINTS: list[TurnPoint] = []
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

        for x, y in compute_bezier_points(control_points, point1.bnop):
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
        if (not n % SETTINGS['EDITOR']['timer-tag-frequency']) or ("drs-start" in p[2]) or ("drs-end" in p[2]):
            TRACK[n][2].insert(0, "timer")



def terminal(stdscr: _curses.window) -> None: # window - 122x24
    curses.curs_set(0)
    stdscr.nodelay(True)

    textbox_win = curses.newwin(1, 117, 12, 5)
    textbox = curses.textpad.Textbox(textbox_win)

    TERMINAL_LATEST_INFO = ""

    command: list[str]

    while 1:
        stdscr.clear()

        curses.textpad.rectangle(stdscr, 0, 1, 5, 45)
        stdscr.addstr(0, 2, " Track info ")
        stdscr.addstr(1, 3, f"amount of points:.. {len(TRACK_POINTS)}")
        stdscr.addstr(2, 3, f"track length:...... {sum([pg.Vector2(TRACK_POINTS[n]).distance_to(TRACK_POINTS[n + 1]) for n in range(len(TRACK_POINTS) - 1)]) * SETTINGS['TRACK']['scale']}")

        if len(TRACK_POINTS) >= 3:
            stdscr.addstr(3, 3, f"starting direction: {pg.Vector2(TRACK_POINTS[0][0] - TRACK_POINTS[-1][0], TRACK_POINTS[0][1] - TRACK_POINTS[-1][1]).normalize()}")
        else:
            stdscr.addstr(3, 3, f"starting direction: (not enough points)")

        stdscr.addstr(4, 3, f"scale:............. {SETTINGS['TRACK']['scale']}")


        curses.textpad.rectangle(stdscr, 6, 1, 10, 45)
        stdscr.addstr(6, 2, " Editor info ")
        # stdscr.addstr(7, 3, f"bnop:............... {SETTINGS['EDITOR']['global -bezier-num-of-points']}")
        stdscr.addstr(7, 3, f"bnop:............... {SETTINGS['EDITOR']['current-bezier-num-of-points']}")
        stdscr.addstr(8, 3, f"timer tag frequency: {SETTINGS['EDITOR']['timer-tag-frequency']}")
        stdscr.addstr(9, 3, f"grid {"size:.......... " + str(SETTINGS['EDITOR']['grid-size']) if SETTINGS['EDITOR']['grid-size'] else "disabled"}")


        curses.textpad.rectangle(stdscr, 0, 46, 10, 122)
        stdscr.addstr(0, 47, " Help ")
        stdscr.addstr(1, 48, "help")
        stdscr.addstr(1, 53, "<command>", curses.A_VERTICAL)
        stdscr.addstr(2, 48, "update")

        stdscr.addstr(3, 48, "bnop") # <n> <*objects>
        stdscr.addstr(3, 53, "<n>", curses.A_BLINK)
        stdscr.addstr(3, 57, "<*objects>", curses.A_BLINK)

        stdscr.addstr(4, 48, "save") # <track name> <racing type> [*author(s)]
        stdscr.addstr(4, 53, "<track name>", curses.A_BLINK)
        stdscr.addstr(4, 66, "<racing type>", curses.A_BLINK)
        stdscr.addstr(4, 80, "[*author(s)]", curses.A_BLINK)

        stdscr.addstr(5, 48, "tag") # <*frequency>
        stdscr.addstr(5, 52, "<*frequency>", curses.A_BLINK)

        stdscr.addstr(6, 48, "grid") # <size>
        stdscr.addstr(6, 53, "<size>", curses.A_BLINK)

        stdscr.addstr(7, 48, "snap") # <*objects>
        stdscr.addstr(7, 53, "<*objects>", curses.A_BLINK)


        curses.textpad.rectangle(stdscr, 11, 1, 13, 122)
        stdscr.addstr(11, 2, " Command line ")
        stdscr.addstr(12, 3, ">")

        stdscr.addstr(15, 3, TERMINAL_LATEST_INFO)
        curses.textpad.rectangle(stdscr, 14, 1, 27, 122)
        stdscr.addstr(14, 2, " Latest info ")

        stdscr.refresh()

        try:
            if stdscr.getkey() == "\n":
                curses.curs_set(1)

                textbox.edit()
                command = textbox.gather().lower().split()

                if not len(command):
                    continue

                match command[0]:
                    case "bnop": # <n> <*objects>
                        if 3 >= len(command) >= 2:
                            if command[1].isdigit() and int(command[1]) > 1:
                                if len(command) == 3:
                                    if command[2] in ["lc", "last-curve"]:
                                        TRACK_TURN_POINTS[-2].bnop = int(command[1])
                                        TERMINAL_LATEST_INFO = f"BNOP: Last curve's bnop set to {TRACK_TURN_POINTS[-2].bnop}."

                                    elif command[2] in ["c", "current"]:
                                        TRACK_TURN_POINTS[-1].bnop = int(command[1])
                                        SETTINGS['EDITOR'].update({'current-bezier-num-of-points': int(command[1])})
                                        TERMINAL_LATEST_INFO = f"BNOP: Set to {SETTINGS['EDITOR']['current-bezier-num-of-points']}."

                                    else:
                                        TERMINAL_LATEST_INFO = f"[!] BNOP: Invalid <*objects> parameter ('{command[1]}' provided)."
                                else:
                                    TRACK_TURN_POINTS[-1].bnop = int(command[1])
                                    SETTINGS['EDITOR'].update({'current-bezier-num-of-points': int(command[1])})
                                    TERMINAL_LATEST_INFO = f"BNOP: Set to {SETTINGS['EDITOR']['current-bezier-num-of-points']}."

                            elif command[1] in ["d", "default"]:
                                TRACK_TURN_POINTS[-1].bnop = 16
                                SETTINGS['EDITOR'].update({'current-bezier-num-of-points': 16})
                                TERMINAL_LATEST_INFO = f"BNOP: Set to {SETTINGS['EDITOR']['current-bezier-num-of-points']}."

                            else:
                                TERMINAL_LATEST_INFO = f"[!] BNOP: First parameter must be a number bigger than 1 ('{command[1]}' provided)."
                        else:
                            TERMINAL_LATEST_INFO = f"[!] BNOP: This command takes atmost 2 parameters ({len(command) - 1} provided)"

                        calculate_track_points()

                    case "tag": # <*frequency>
                        TERMINAL_LATEST_INFO = ""

                        if len(command) == 2:
                            if command[1].isdigit() and int(command[1]) > 1:
                                SETTINGS['EDITOR'].update({'timer-tag-frequency': int(command[1])})
                                TERMINAL_LATEST_INFO = f"TAG: Default tag frequency was to {SETTINGS['EDITOR']['timer-tag-frequency']}.\n   "
                            else:
                                TERMINAL_LATEST_INFO = f"[!] TAG: Parameter must be a number bigger than 1 ('{command[1]}' provided)."
                        elif len(command) > 2:
                            TERMINAL_LATEST_INFO = f"[!] TAG: This command takes 1 (optional) parameter ({len(command) - 1} provided)."

                        tag_track()
                        TERMINAL_LATEST_INFO += "TAG: Track tagged."

                    case "grid": # <size>
                        if len(command) == 2:
                            if command[1].isdigit() and int(command[1]) >= 0:
                                SETTINGS['EDITOR'].update({'grid-size': int(command[1])})
                                TERMINAL_LATEST_INFO = f"GRID: Grid set to {SETTINGS['EDITOR']['grid-size']}."
                            else:
                                TERMINAL_LATEST_INFO = f"[!] GRID: Parameter must be a positive number ('{command[1]}' provided)."
                        else:
                            TERMINAL_LATEST_INFO = f"[!] GRID: This command takes 1 parameter ({len(command) - 1} provided)."

                    case "snap": # <*objects>
                        if SETTINGS['EDITOR']['grid-size']:
                            if len(command) <= 2:
                                for n, p in enumerate(TRACK_TURN_POINTS):
                                    _cache_turn_point_xy = p.xy

                                    if (len(command[1]) < 2) or (command[1] in ["g", "global"]) or (command[1] in ["p", "turn-points"]):
                                        TRACK_TURN_POINTS[n].x, TRACK_TURN_POINTS[n].y = snap_point_to_grid(p.xy)

                                    if (len(command[1]) < 2) or (command[1] in ["g", "global"]) or (command[1] in ["c", "turn-checkpoints"]):
                                        TRACK_TURN_POINTS[n].cx0 += TRACK_TURN_POINTS[n].x -_cache_turn_point_xy[0]
                                        TRACK_TURN_POINTS[n].cy0 += TRACK_TURN_POINTS[n].y -_cache_turn_point_xy[1]

                                        TRACK_TURN_POINTS[n].cx1 += TRACK_TURN_POINTS[n].x -_cache_turn_point_xy[0]
                                        TRACK_TURN_POINTS[n].cy1 += TRACK_TURN_POINTS[n].y -_cache_turn_point_xy[1]
                                else:
                                    del _cache_turn_point_xy
                                    TERMINAL_LATEST_INFO = f"SNAP: Snapped {"turn-points" if (command[1] in ["p", "turn-points"]) else "turn-checkpoints" if (command[1] in ["c", "turn-checkpoints"]) else "everything"} to the grid."
                            else:
                                TERMINAL_LATEST_INFO = f"[!] SNAP: This command takes 1 (optional) parameter ({len(command) - 1} provided)."
                        else:
                            TERMINAL_LATEST_INFO = "[!] SNAP: Grid has not been set."

                        calculate_track_points()

                    case "clear":
                        TERMINAL_LATEST_INFO = ""

                    case "update":
                        if len(command) == 1:
                            calculate_track_points()
                            TERMINAL_LATEST_INFO = "UPDATE: Updated track."
                        else:
                            TERMINAL_LATEST_INFO = f"[!] UPDATE: This command takes no parameters."

                    case "save": # <track name> <racing type> [*author(s)]
                        if len(command) < 2 + 1:
                            TERMINAL_LATEST_INFO = f"[!] SAVE: This command takes atleast 2 parameters ({len(command) - 1} provided)."
                            continue
                        if not command[2] in ["formula", "rallycross"]:
                            TERMINAL_LATEST_INFO = f"[!] SAVE: <racing type> parameter is not valid ('{command[2]}' provided)."
                            continue

                        path_to_file = path.abspath(path.join("src", "data", "tracks", command[1]))


                        final_track: list[list] = []
                        for n1, p in enumerate(TRACK):
                            for n2, tp1 in enumerate(TRACK_TURN_POINTS):
                                if tp1.index == n1:
                                    final_track.append([tp1.x, tp1.y, ["turn-end", "turn-start"]])
                                    break
                            else:
                                final_track.append(p)
                        else:
                            del n1, tp1, n2, p


                        # final_track: list[list] = []
                        # for n, p in enumerate(TRACK):
                        #     if n == 0:
                        #         final_track.append(p)
                        #         continue

                        #     if n == len(TRACK) - 1:
                        #         _temp_p2: list = p[2]
                        #         _temp_p2.insert(0, "lap-end")

                        #         if "timer" not in _temp_p2:
                        #             _temp_p2.insert(0, "timer")

                        #         final_track.append([p[0], p[1], _temp_p2])
                        #         continue

                        #     _temp_ttp_end = False
                        #     for tp in TRACK_TURN_POINTS:
                        #         if (p[0], p[1]) == tp.xy:
                        #             _temp_p2: list = p[2]

                        #             _temp_p2.append("turn-end")
                        #             final_track[n - 1][2].append("acceleration-start-point")

                        #             _temp_p2.append("turn-start")
                        #             final_track.append([p[0], p[1], _temp_p2])

                        #             _temp_ttp_end = True
                        #             break
                        #     if _temp_ttp_end:
                        #         continue

                        #     if "turn-start" in final_track[n - 1][2]:
                        #         _temp_p2: list = p[2]
                        #         _temp_p2.append("braking-finish-point")
                        #         _temp_p2.append({"reference-target-speed": 0, "overtaking-risk": 0.0})
                        #         final_track.append([p[0], p[1], _temp_p2])
                        #         continue

                        #     final_track.append(p)
                        # else:
                        #     del _temp_p2, _temp_ttp_end


                        while 1:
                            try:
                                with open(path_to_file, "r") as file:
                                    final_file: dict = json.load(file)

                                    if not command[2] in final_file['allowed-racing-types']:
                                        final_file['allowed-racing-types'].append(command[2])

                                    if len(command) > 3:
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

                                            "track": final_track
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

                                TERMINAL_LATEST_INFO = f"SAVE: Track saved as '{command[1]}' ({command[2]}) by {command[3]}."
                                del final_track, final_file, path_to_file
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
                        continue

                    case "help":
                        if len(command) > 1:
                            match command[1]:
                                case "save": # <track name> <racing type> [*author(s)]
                                    TERMINAL_LATEST_INFO = """Command `save` saves track to a specified file.

    syntax:
        save <track name> <racing type> [*author(s)]

    parameters:
        <track name>  - name of the track and the file in which it will be saved with no spaces
        <racing type> - racing type to create or update in a given file
        ├ 'formula'
        └ 'rallycross'
        [*author(s)]  - authors' names split with spaces
"""

                                case "clear":
                                    TERMINAL_LATEST_INFO = """Command `clear` clears latest info.

    syntax:
        clear
"""

                                case "snap": # <*objects>
                                    TERMINAL_LATEST_INFO = """Command `snap` snaps specified points to the grid.

    syntax:
        snap <*objects>

    parameters:
        <*objects> - objects to which the change will be applied
        ├ 'all', 'a' (default)
        ├ 'turn-points', 'p'
        └ 'turn-checkpoints', 'c'
"""

                                case "grid": # <size>
                                    TERMINAL_LATEST_INFO = """Command `grid` allows the user to set the grid size.

    syntax:
        grid <size>

    parameters:
        <size> - cell side length in pixels
"""

                                case "tag": # <*frequency>
                                    TERMINAL_LATEST_INFO = """Command `tag` allows the user to auto-tag points and change the default 'timer' tag frequency.\n   If the <*frequency> parameter is specified, the command will auto-tag points and change default 'timer' tag frequency.

    syntax:
        tag <*frequency>

    parameters:
        <*frequency> - TODO
""" # TODO

                                case "bnop": # <n> <*objects>
                                    TERMINAL_LATEST_INFO = """Command `bnop` allows the user to set the number of points in curves.

    syntax:
        bnop <n> <*objects>

    parameters:
        <n>        - number of points
        <*objects> - objects to which the change will be applied
        ├ 'global, 'g'       - changes the global bnop setting (default)
        ├ 'all', 'a'         - changes bnop setting for whole current track but does not change the global bnop setting
        └ 'next-curve', 'nc' - temporarily changes the bnop setting (only for the next curve) but does not affect rest of the track nor the global bnop setting
"""

                                case "update":
                                    TERMINAL_LATEST_INFO = """Command `update` recalculates whole track.

    syntax:
        update
"""

                                case "help":
                                    TERMINAL_LATEST_INFO = """Command `help` shows extended info about specific command.

    syntax:
        help <command>

    parameters:
        <command> - name of any command
"""
                        else:
                            TERMINAL_LATEST_INFO = f"[!] HELP: command requires one parameter ({len(command)} provided)."

                    case _other:
                        TERMINAL_LATEST_INFO = f"[!] Command `{_other}` does not exist."
                        del _other

        except _curses.error: pass
        finally:
            textbox_win.clear()
            curses.curs_set(0)


_thread_terminal = Thread(target=curses.wrapper, args=[terminal], name="thread-terminal", daemon=True)
_thread_terminal.start()



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
                if temp_selected_point:
                    TRACK_TURN_POINTS[temp_selected_point].x += e.rel[0]
                    TRACK_TURN_POINTS[temp_selected_point].y += e.rel[1]

                    TRACK_TURN_POINTS[temp_selected_point].cx0 += e.rel[0]
                    TRACK_TURN_POINTS[temp_selected_point].cy0 += e.rel[1]

                    TRACK_TURN_POINTS[temp_selected_point].cx1 += e.rel[0]
                    TRACK_TURN_POINTS[temp_selected_point].cy1 += e.rel[1]

                    calculate_track_points()

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
                    if KEY_PRESSED[pg.K_LALT]:
                        temp_mouse_down_point = e.pos
                    else:
                        temp_mouse_down_point = snap_point_to_grid(e.pos)

                elif e.button == 3:
                    temp_mouse_down_info = ["dirt"]
                    if KEY_PRESSED[pg.K_LALT]:
                        temp_mouse_down_point = e.pos
                    else:
                        temp_mouse_down_point = snap_point_to_grid(e.pos)

        if e.type == pg.MOUSEBUTTONUP:
            if temp_mouse_down_point and temp_mouse_down_info:
                if ((e.button == 1) and ("asphalt" in temp_mouse_down_info)) or ((e.button == 3) and ("dirt" in temp_mouse_down_info)):
                    if KEY_PRESSED[pg.K_LALT]:
                        TRACK_TURN_POINTS.append(TurnPoint(temp_mouse_down_point, MOUSE_POS, (temp_mouse_down_point[0] + (temp_mouse_down_point[0] - MOUSE_POS[0]), temp_mouse_down_point[1] + (temp_mouse_down_point[1] - MOUSE_POS[1])), temp_mouse_down_info))
                    else:
                        TRACK_TURN_POINTS.append(TurnPoint(temp_mouse_down_point, snap_point_to_grid(MOUSE_POS), snap_point_to_grid((temp_mouse_down_point[0] + (temp_mouse_down_point[0] - snap_n_to_grid(MOUSE_POS[0])), temp_mouse_down_point[1] + (temp_mouse_down_point[1] - snap_n_to_grid(MOUSE_POS[1])))), temp_mouse_down_info))

            temp_selected_point = temp_selected_checkpoint = temp_mouse_down_point = temp_mouse_down_info = None
            calculate_track_points()


    WIN.fill("white")


    if SETTINGS['EDITOR']['grid-size']:
        for n in range(SETTINGS['EDITOR']['grid-size'], 1000 - SETTINGS['EDITOR']['grid-size'] + 1, SETTINGS['EDITOR']['grid-size']):
            pg.draw.line(WIN, "gray80", (n, 0), (n, 1000))
            pg.draw.line(WIN, "gray80", (0, n), (1000, n))


    if (temp_selected_point) and (not KEY_PRESSED[pg.K_LALT]):
        TRACK_TURN_POINTS[temp_selected_point].cx0, TRACK_TURN_POINTS[temp_selected_point].cy0 = TRACK_TURN_POINTS[temp_selected_point].cx0 - (TRACK_TURN_POINTS[temp_selected_point].x - MOUSE_POS[0]), TRACK_TURN_POINTS[temp_selected_point].cy0 - (TRACK_TURN_POINTS[temp_selected_point].y - MOUSE_POS[1])
        TRACK_TURN_POINTS[temp_selected_point].cx1, TRACK_TURN_POINTS[temp_selected_point].cy1 = TRACK_TURN_POINTS[temp_selected_point].cx1 - (TRACK_TURN_POINTS[temp_selected_point].x - MOUSE_POS[0]), TRACK_TURN_POINTS[temp_selected_point].cy1 - (TRACK_TURN_POINTS[temp_selected_point].y - MOUSE_POS[1])
        TRACK_TURN_POINTS[temp_selected_point].x,   TRACK_TURN_POINTS[temp_selected_point].y   = MOUSE_POS

        TRACK_TURN_POINTS[temp_selected_point].x,   TRACK_TURN_POINTS[temp_selected_point].y   = snap_point_to_grid(TRACK_TURN_POINTS[temp_selected_point].xy)
        TRACK_TURN_POINTS[temp_selected_point].cx0, TRACK_TURN_POINTS[temp_selected_point].cy0 = snap_point_to_grid((TRACK_TURN_POINTS[temp_selected_point].cx0, TRACK_TURN_POINTS[temp_selected_point].cy0))
        TRACK_TURN_POINTS[temp_selected_point].cx1, TRACK_TURN_POINTS[temp_selected_point].cy1 = snap_point_to_grid((TRACK_TURN_POINTS[temp_selected_point].cx1, TRACK_TURN_POINTS[temp_selected_point].cy1))

        calculate_track_points()


    if (temp_selected_checkpoint) and (not KEY_PRESSED[pg.K_LALT]):
        exec(
            f"TRACK_TURN_POINTS[temp_selected_checkpoint[0]].cx{temp_selected_checkpoint[1]}, TRACK_TURN_POINTS[temp_selected_checkpoint[0]].cy{temp_selected_checkpoint[1]} = MOUSE_POS;"
            f"TRACK_TURN_POINTS[temp_selected_checkpoint[0]].cx{temp_selected_checkpoint[1]}, TRACK_TURN_POINTS[temp_selected_checkpoint[0]].cy{temp_selected_checkpoint[1]} = snap_point_to_grid((TRACK_TURN_POINTS[temp_selected_checkpoint[0]].cx{temp_selected_checkpoint[1]}, TRACK_TURN_POINTS[temp_selected_checkpoint[0]].cy{temp_selected_checkpoint[1]}));"
        )

        calculate_track_points()


    if temp_mouse_down_point and temp_mouse_down_info:
        if KEY_PRESSED[pg.K_LALT]:
            _temp_checkpoint_0 = MOUSE_POS
            _temp_checkpoint_1 = (temp_mouse_down_point[0] + (temp_mouse_down_point[0] - MOUSE_POS[0]), temp_mouse_down_point[1] + (temp_mouse_down_point[1] - MOUSE_POS[1]))
        else:
            _temp_checkpoint_0 = snap_point_to_grid(MOUSE_POS)
            _temp_checkpoint_1 = snap_point_to_grid((temp_mouse_down_point[0] + (temp_mouse_down_point[0] - snap_n_to_grid(MOUSE_POS[0])), temp_mouse_down_point[1] + (temp_mouse_down_point[1] - snap_n_to_grid(MOUSE_POS[1]))))

        TRACK_TURN_POINTS.append(TurnPoint(temp_mouse_down_point, _temp_checkpoint_0, _temp_checkpoint_1, temp_mouse_down_info))
        calculate_track_points()

        pg.draw.line(WIN, "red", temp_mouse_down_point, _temp_checkpoint_0)
        pg.draw.line(WIN, "red", temp_mouse_down_point, _temp_checkpoint_1)

        pg.draw.circle(WIN, "red", _temp_checkpoint_0, 4)
        pg.draw.circle(WIN, "red", _temp_checkpoint_1, 4)

        if "asphalt" in temp_mouse_down_info:
            pg.draw.circle(WIN, "aqua", temp_mouse_down_point, 2)
        elif "dirt" in temp_mouse_down_info:
            pg.draw.circle(WIN, "orange", temp_mouse_down_point, 2)

        del _temp_checkpoint_0, _temp_checkpoint_1


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