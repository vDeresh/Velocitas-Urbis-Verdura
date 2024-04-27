import sys
import pygame as pg
# from os import system # TODO


_equal_drivers       = "--eq"  in sys.argv
_same_starting_point = "--ssp" in sys.argv
_show_track_data     = "--td"  in sys.argv
_update_in_realtime  = "--uir" in sys.argv # for simulation
_racing_allowed      = "--ra"  in sys.argv
_console_only        = "--co"  in sys.argv # TODO
_half_of_the_grid    = "--h"   in sys.argv
_laps                = None
_fps                 = 0 # for simulation
_pit                 = False

for np, p in enumerate(sys.argv):
    if p == "--fps":
        _fps = int(sys.argv[np + 1])
        break

for np, p in enumerate(sys.argv):
    if p == "--pit":
        _pit = int(sys.argv[np + 1])
        break

for np, p in enumerate(sys.argv):
    if p == "--laps":
        _laps = int(sys.argv[np + 1])
        break


from src.code.game.racesim import simulation
from src.code.manager import team  as mgr_team
from src.code.manager import track as mgr_track
from src.code.classes import Driver
from src.code.config  import FONT_1, WIN

from threading import Thread


def simulation_interface(track_name: str, DRIVERS: list[Driver]) -> None:
    _longest_name_length = len(max(DRIVERS, key=lambda x: len(x.name)).name)

    if _pit:
        for driver in DRIVERS:
            driver.decision_stack.append({"type": "pit", "tyre": _pit})

    if _half_of_the_grid:
        DRIVERS = DRIVERS[1::2]


    TRACK_INFO = mgr_track.track_show()[track_name]['info']

    TRACK = mgr_track.track_show()[track_name]['track']
    PITLANE = mgr_track.track_show()[track_name]['pit-lane']

    TRACK_POINTS = mgr_track.convert_track_to_points(TRACK)
    PITLANE_POINTS = mgr_track.convert_track_to_points(PITLANE)

    TRACK_POINTS_SCALED = mgr_track.scale_track_points(TRACK_POINTS)
    PITLANE_POINTS_SCALED = mgr_track.scale_track_points(PITLANE_POINTS)


    for n, driver in enumerate(DRIVERS):
        driver.init(TRACK, n + 1, 0, _racing_allowed)
        if _same_starting_point:
            driver.set_pos(TRACK_POINTS[0][0], TRACK_POINTS[0][1])
        else:
            driver.set_pos(TRACK_POINTS[0][0] - 12 * TRACK_INFO['starting-direction'][0] * (n + 1), TRACK_POINTS[0][1] - 12 * TRACK_INFO['starting-direction'][1] * (n + 1))


    SHARED = {
        "fps": 0,
        "lap": 0
    }

    _thread_simulation = Thread(target=simulation, name="simulation-thread", args=[_fps, _update_in_realtime, SHARED, TRACK, TRACK_POINTS, TRACK_INFO, PITLANE, PITLANE_POINTS, DRIVERS], daemon=True)
    _thread_simulation.start()

    if not _console_only:
        while 1:
            for e in pg.event.get():
                if e.type == pg.QUIT:
                    pg.quit()
                    exit()

            WIN.fill("black")
            pg.draw.aalines(WIN, "azure1", True, TRACK_POINTS_SCALED)
            pg.draw.aalines(WIN, "azure4", False, PITLANE_POINTS_SCALED)
            pg.draw.rect(WIN, "red", (TRACK_POINTS_SCALED[0][0] - 1, TRACK_POINTS_SCALED[0][1] - 1, 4, 4), 2)

            for driver in DRIVERS:
                if driver.tyre_type == 0:
                    pg.draw.circle(WIN, "#ff7a7a", driver.pos / 2, 3)
                elif driver.tyre_type == 1:
                    pg.draw.circle(WIN, "#c61010", driver.pos / 2, 3)
                elif driver.tyre_type == 2:
                    pg.draw.circle(WIN, "#ffcf24", driver.pos / 2, 3)
                elif driver.tyre_type == 3:
                    pg.draw.circle(WIN, "#f2f2f2", driver.pos / 2, 3)
                elif driver.tyre_type == 4:
                    pg.draw.circle(WIN, "#21ad46", driver.pos / 2, 3)
                elif driver.tyre_type == 5:
                    pg.draw.circle(WIN, "#0050d1", driver.pos / 2, 3)

                pg.draw.circle(WIN, driver.team.color, driver.pos / 2, 2)


            if _show_track_data:
                for n, p in enumerate(PITLANE_POINTS_SCALED):
                    if "speed-limit-start" in PITLANE[n][2] or "speed-limit-end" in PITLANE[n][2]:
                        pg.draw.circle(WIN, "yellow",  (p[0], p[1]), 3)

                    if "pit-box" in PITLANE[n][2]:
                        pg.draw.circle(WIN, "pink", (p[0], p[1]), 3)

                    pg.draw.circle(WIN, "darkred", (p[0], p[1]), 1)

                for n, p in enumerate(TRACK_POINTS_SCALED):
                    if "turn-end" in TRACK[n][2]:
                        pg.draw.circle(WIN, "red",  (p[0], p[1]), 4)

                    if "turn-start" in TRACK[n][2]:
                        pg.draw.circle(WIN, "lime", (p[0], p[1]), 3)

                    pg.draw.circle(WIN, "darkred", (p[0], p[1]), 1)

            WIN.blit(FONT_1.render(str(SHARED['fps']), True, "white"), (0, 0))
            WIN.blit(FONT_1.render(str(SHARED['lap']), True, "white"), (0, 26))

            pg.display.flip()

            if _laps:
                if SHARED['lap'] > _laps:
                    break

    else:
        pg.quit()
        # _thread_console_input = Thread(target=None, name="thread-console-input", daemon=True)
        # _thread_console_input.start()
        while 1:
            # print(SHARED['fps'])
            user_command = input(">")
            match user_command:
                case "stop":
                    break
                case "info":
                    for driver in DRIVERS:
                        print(
                            "\n"
                            f"{driver.name} ({driver.number})", "\n"
                            f"Speed:         {driver.speed * 60}", "\n"
                            f"Current lap:   {driver.lap}", "\n"
                            f"Current pos:   {driver.pos}", "\n"
                            f"Race position: {driver.position}", "\n"
                        )

                    print(f"\nCurrent standings (lap {DRIVERS[0].lap})")
                    for n in range(len(DRIVERS) // 2):
                        d1 = DRIVERS[n]

                        if d1.position < d1.number:
                            d1_string = f"{d1.position:02} ↑ {"".join(" " for _ in range(_longest_name_length - len(d1.name)))}{d1.name}"
                        elif d1.position > d1.number:
                            d1_string = f"{d1.position:02} ↓ {"".join(" " for _ in range(_longest_name_length - len(d1.name)))}{d1.name}"
                        else:
                            d1_string = f"{d1.position:02} → {"".join(" " for _ in range(_longest_name_length - len(d1.name)))}{d1.name}"

                        try:
                            d2 = DRIVERS[n + len(DRIVERS) // 2]

                            if d2.position < d2.number:
                                d2_string = f"{d2.position:02} ↑ {"".join(" " for _ in range(_longest_name_length - len(d2.name)))}{d2.name}"
                            elif d2.position > d2.number:
                                d2_string = f"{d2.position:02} ↓ {"".join(" " for _ in range(_longest_name_length - len(d2.name)))}{d2.name}"
                            else:
                                d2_string = f"{d2.position:02} → {"".join(" " for _ in range(_longest_name_length - len(d2.name)))}{d2.name}"
                        except IndexError:
                            d2_string = ""

                        print(
                            d1_string,
                            " | ",
                            d2_string
                        )
            # system("cls") # TODO

            # sys.stdout.write("\nConsole only mode\n")
            # sys.stdout.writelines(["\n"
            #     "Settings", "\n"
            #     "Equal drivers: ", str(_equal_drivers), "\n"
            #     "Same starting point: ", str(_same_starting_point), "\n"
            #     "Show track data: ", str(_show_track_data), "\n"
            #     "Update in realtime: ", str(_update_in_realtime), "\n"
            #     "Racing allowed: ", str(_racing_allowed), "\n"
            #     "Pit: ", str(_pit), "\n"
            #     "Laps: ", str(_laps), "\n"
            # ])

    print()
    print("Summary") # TODO
    print()

    for driver in DRIVERS:
        print(
            "\n"
            f"{driver.name} ({driver.number})", "\n"
            f"Speed:         {driver.speed * 60}", "\n"
            f"Current lap:   {driver.lap}", "\n"
            f"Current pos:   {driver.pos}", "\n"
            f"Race position: {driver.position}", "\n"
        )

    print(f"\nCurrent standings (lap {DRIVERS[0].lap})")
    for n in range(len(DRIVERS) // 2):
        d1 = DRIVERS[n]

        if d1.position < d1.number:
            d1_string = f"{d1.position:02} ↑ {"".join(" " for _ in range(_longest_name_length - len(d1.name)))}{d1.name}"
        elif d1.position > d1.number:
            d1_string = f"{d1.position:02} ↓ {"".join(" " for _ in range(_longest_name_length - len(d1.name)))}{d1.name}"
        else:
            d1_string = f"{d1.position:02} → {"".join(" " for _ in range(_longest_name_length - len(d1.name)))}{d1.name}"

        try:
            d2 = DRIVERS[n + len(DRIVERS) // 2]

            if d2.position < d2.number:
                d2_string = f"{d2.position:02} ↑ {"".join(" " for _ in range(_longest_name_length - len(d2.name)))}{d2.name}"
            elif d2.position > d2.number:
                d2_string = f"{d2.position:02} ↓ {"".join(" " for _ in range(_longest_name_length - len(d2.name)))}{d2.name}"
            else:
                d2_string = f"{d2.position:02} → {"".join(" " for _ in range(_longest_name_length - len(d2.name)))}{d2.name}"
        except IndexError:
            d2_string = ""

        print(d1_string, " | ", d2_string)


if _equal_drivers:
    simulation_interface("sc1", mgr_team.ready_equal_drivers())
else:
    simulation_interface("sc1", mgr_team.ready_drivers())



# Current standings (lap 147)
# 01 ↑ Driver 17  |  06 ↑ Driver 13
# 02 ↑ Driver 19  |  07 → Driver 07
# 03 ↑ Driver 15  |  08 ↓ Driver 05
# 04 ↑ Driver 11  |  09 ↓ Driver 01
# 05 ↑ Driver 09  |  10 ↓ Driver 03


# Current standings (lap 147)
# 01 ↑ Driver 17  |  06 ↑ Driver 13
# 02 ↑ Driver 19  |  07 → Driver 07
# 03 ↑ Driver 15  |  08 ↓ Driver 05
# 04 ↑ Driver 11  |  09 ↓ Driver 01
# 05 ↑ Driver 09  |  10 ↓ Driver 03


# Current standings (lap 300)
# 01 ↑ Driver 17  |  06 ↑ Driver 13
# 02 ↑ Driver 19  |  07 → Driver 07
# 03 ↑ Driver 15  |  08 ↓ Driver 05
# 04 ↑ Driver 11  |  09 ↓ Driver 01
# 05 ↑ Driver 09  |  10 ↓ Driver 03