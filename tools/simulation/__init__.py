import sys
import json
from os import path

from config import *
from classes import Team, Driver


if len(sys.argv) <= 1:
    sys.argv.append("sc1")
    sys.argv.append("a")
    sys.argv.append("1")
    sys.argv.append("0")

FPS = int(sys.argv[4])


def show():
    with open(path.abspath(path.join("tools", "simulation", "data", "tracks")), "r") as file:
        return json.load(file)


def convert_track_to_points(track: list[list]):
    TRACK_POINTS = [(x, y) for x, y, *_ in track]
    return TRACK_POINTS


def team_show() -> dict:
    with open(path.abspath(path.join("tools", "simulation", "data", "teams")), "r") as file:
        return json.load(file)


def driver_show() -> dict:
    with open(path.abspath(path.join("tools", "simulation", "data", "drivers")), "r") as file:
        return json.load(file)


def ready_drivers() -> list:
    DRIVERS: list[Driver] = []

    for team in (teams := team_show()):
        for driver in (drivers := driver_show()):
            for n in teams[team]['drivers']:
                if n == drivers[driver]['number']:
                    DRIVERS.append(Driver(Team(team, teams[team]['drivers'], teams[team]['color'], teams[team]['name-abbreviation'], teams[team]['car-stats']), drivers[driver]['number'], drivers[driver]['skills']))

    return DRIVERS





def simulation(track_name: str, DRIVERS: list[Driver]) -> None:
    TRACK_INFO = show()[track_name]['info']

    TRACK = show()[track_name]['track']
    TRACK_POINTS = convert_track_to_points(TRACK)

    PITLANE = show()[track_name]['pit-lane']
    PITLANE_POINTS = convert_track_to_points(PITLANE)


    match sys.argv[2]:
        case "a":
            pass
        case "s":
            DRIVERS = DRIVERS[::2]
        case "o":
            DRIVERS = [DRIVERS[0]]
        case "t":
            DRIVERS = [DRIVERS[0], DRIVERS[-1]]


    for n, driver in enumerate(DRIVERS):
        if int(sys.argv[3]):
            driver.set_pos(TRACK_POINTS[0][0] - 12 * TRACK_INFO['starting-direction'][0] * (n + 1), TRACK_POINTS[0][1] - 12 * TRACK_INFO['starting-direction'][1] * (n + 1))
        else:
            driver.set_pos(TRACK_POINTS[0][0], TRACK_POINTS[0][1])
        driver.init(TRACK, n + 1)

    LAP = 0

    clock = pg.Clock()
    while 1:
        clock.tick(FPS)

        for e in pg.event.get():
            if e.type == pg.QUIT:
                pg.quit()
                exit()

        for n, driver in enumerate(DRIVERS):
            driver.position = n + 1
            driver.update(TRACK, TRACK_POINTS, DRIVERS)


        WIN.fill("black")
        pg.draw.aalines(WIN, "azure1", True, TRACK_POINTS)
        pg.draw.aalines(WIN, "azure4", False, PITLANE_POINTS)

        for driver in DRIVERS:
            driver.post_update()
            pg.draw.circle(WIN, driver.team.color, driver.pos, 4)

        WIN.blit(FONT_1.render("FPS: " + str(int(clock.get_fps())), True, "white"), (0, 0))
        WIN.blit(FONT_1.render("LAP: " + str(LAP), True, "white"), (0, 26))
        # WIN.blit(FONT_1.render(str(distance_to_next_driver(TRACK_POINTS, DRIVERS[1], DRIVERS)), True, "white"), (0, 26))
        # WIN.blit(FONT_1.render(str(DRIVERS[0].speed * 2 * 60), True, "white"), (0, 26))
        # WIN.blit(FONT_1.render(str(DRIVERS[-1].speed * 2 * 60), True, "white"), (0, 50))

        pg.draw.rect(WIN, "red", (TRACK_POINTS[0][0] - 1, TRACK_POINTS[0][1] - 1, 4, 4), 2)
        pg.display.flip()

        DRIVERS.sort(key=lambda x: (x.lap, x.current_point, -x.pos.distance_to(x.next_point_xy), x.speed), reverse=True) # the bigger the better
        LAP = DRIVERS[0].lap


simulation(sys.argv[1], ready_drivers())