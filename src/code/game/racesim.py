from ..config import *
from ..manager import track as mgr_track
from ..manager import team as mgr_team
from ..classes import Team, Driver, distance_to_next_driver
# from ..others import calculate_pit_entry_point as init_others

from threading import Thread


def simulation(shared, TRACK, TRACK_POINTS, TRACK_INFO, PITLANE, PITLANE_POINTS, DRIVERS: list[Driver]) -> None:
    # DRIVERS = DRIVERS[:2:]
    # DRIVERS = [DRIVERS[0]]
    # DRIVERS = [DRIVERS[0], DRIVERS[-1]]
    # DRIVERS = DRIVERS[::2]

    # print(TRACK)
    # print(DRIVERS)
    # print()

    # LAP = 0

    clock = pg.Clock()
    while 1:
        clock.tick(FPS)

        prev_DRIVERS = DRIVERS

        for n, driver in enumerate(DRIVERS):
            driver.position = n + 1
            driver.update(TRACK, TRACK_POINTS, PITLANE, PITLANE_POINTS, TRACK_INFO, prev_DRIVERS)

        # for driver in DRIVERS:
        #     driver.post_update()

        DRIVERS.sort(key=lambda x: (x.lap, x.current_point, -x.pos.distance_to(x.next_point_xy), x.speed), reverse=True) # the bigger the better
        # LAP = DRIVERS[0].lap
        shared["lap"] = DRIVERS[0].lap
        shared["fps"] = clock.get_fps()


def simulation_interface(track_name: str, DRIVERS: list[Driver]) -> None:
    # DRIVERS = DRIVERS[::2]
    # DRIVERS = [DRIVERS[0], DRIVERS[1]]
    # DRIVERS = [DRIVERS[0]]
    # DRIVERS = DRIVERS[:4]

    # for driver in DRIVERS:
    #     driver.decision_stack.append({"type": "pit", "tyre": 0})

    TRACK_INFO = mgr_track.show()[track_name]['info']

    TRACK = mgr_track.show()[track_name]['track']
    PITLANE = mgr_track.show()[track_name]['pit-lane']

    TRACK_POINTS = mgr_track.convert_track_to_points(TRACK)
    PITLANE_POINTS = mgr_track.convert_track_to_points(PITLANE)

    TRACK_POINTS_SCALED = mgr_track.scale_track_points(TRACK_POINTS)
    PITLANE_POINTS_SCALED = mgr_track.scale_track_points(PITLANE_POINTS)


    for n, driver in enumerate(DRIVERS):
        driver.init(TRACK, n + 1, 0)
        driver.set_pos(TRACK_POINTS[0][0] - 16 * TRACK_INFO['starting-direction'][0] * (n + 1), TRACK_POINTS[0][1] - 16 * TRACK_INFO['starting-direction'][1] * (n + 1))
        # driver.set_pos(TRACK_POINTS[0][0], TRACK_POINTS[0][1])

    # DRIVERS[0].tyre_type = 0
    # DRIVERS[1].tyre_type = 1
    # DRIVERS[2].tyre_type = 2
    # DRIVERS[3].tyre_type = 3


    SHARED = {
        "fps": 0,
        "lap": 0
    }

    _thread_simulation = Thread(target=simulation, name="simulation-thread", args=[SHARED, TRACK, TRACK_POINTS, TRACK_INFO, PITLANE, PITLANE_POINTS, DRIVERS], daemon=True)
    _thread_simulation.start()

    while 1:
        for e in pg.event.get():
            if e.type == pg.QUIT:
                pg.quit()
                exit()

        WIN.fill("black")
        pg.draw.aalines(WIN, "azure1", True, TRACK_POINTS_SCALED)
        pg.draw.aalines(WIN, "azure4", False, PITLANE_POINTS_SCALED)
        pg.draw.rect(WIN, "red", (TRACK_POINTS_SCALED[0][0] - 1, TRACK_POINTS_SCALED[0][1] - 1, 4, 4), 2)

        # for driver in DRIVERS:
        #     if driver.tyre_type == 0:
        #         pg.draw.circle(WIN, "#ff7a7a", driver.pos / 2, 3)
        #     elif driver.tyre_type == 1:
        #         pg.draw.circle(WIN, "#c61010", driver.pos / 2, 3)
        #     elif driver.tyre_type == 2:
        #         pg.draw.circle(WIN, "#ffcf24", driver.pos / 2, 3)
        #     elif driver.tyre_type == 3:
        #         pg.draw.circle(WIN, "#f2f2f2", driver.pos / 2, 3)
        #     elif driver.tyre_type == 4:
        #         pg.draw.circle(WIN, "#21ad46", driver.pos / 2, 3)
        #     elif driver.tyre_type == 5:
        #         pg.draw.circle(WIN, "#0050d1", driver.pos / 2, 3)

        for driver in DRIVERS:
            if driver.tyre_type == 0:
                pg.draw.circle(WIN, "#ff7a7a", driver.pos / 2, 2)
            elif driver.tyre_type == 1:
                pg.draw.circle(WIN, "#c61010", driver.pos / 2, 2)
            elif driver.tyre_type == 2:
                pg.draw.circle(WIN, "#ffcf24", driver.pos / 2, 2)
            elif driver.tyre_type == 3:
                pg.draw.circle(WIN, "#f2f2f2", driver.pos / 2, 2)
            elif driver.tyre_type == 4:
                pg.draw.circle(WIN, "#21ad46", driver.pos / 2, 2)
            elif driver.tyre_type == 5:
                pg.draw.circle(WIN, "#0050d1", driver.pos / 2, 2)
            pg.draw.circle(WIN, driver.team.color, driver.pos / 2, 1)

        # for n, p in enumerate(PITLANE_POINTS_SCALED):
        #     if "speed-limit-start" in PITLANE[n][2] or "speed-limit-end" in PITLANE[n][2]:
        #         pg.draw.circle(WIN, "yellow",  (p[0], p[1]), 3)

        #     if "pit-box" in PITLANE[n][2]:
        #         pg.draw.circle(WIN, "pink", (p[0], p[1]), 3)

        #     pg.draw.circle(WIN, "darkred", (p[0], p[1]), 1)
        #     # WIN.blit(FONT.render(str(n), False, "darkred"), (p[0], p[1]))


        # for n, p in enumerate(TRACK_POINTS_SCALED):
        #     if "turn-end" in TRACK[n][2]:
        #         pg.draw.circle(WIN, "red",  (p[0], p[1]), 4)

        #     if "turn-start" in TRACK[n][2]:
        #         pg.draw.circle(WIN, "lime", (p[0], p[1]), 3)

        #     pg.draw.circle(WIN, "darkred", (p[0], p[1]), 1)
        #     # WIN.blit(FONT.render(str(n), False, "darkred"), (p[0], p[1]))

        WIN.blit(FONT_1.render(str(SHARED['fps']), True, "white"), (0, 0))
        WIN.blit(FONT_1.render(str(SHARED['lap']), True, "white"), (0, 26))
        # WIN.blit(FONT_1.render(str(DRIVERS[0].tyre_wear), True, "white"), (0, 26))
        # WIN.blit(FONT_1.render(str(DRIVERS[1].tyre_wear), True, "white"), (0, 50))
        # WIN.blit(FONT_1.render(str(distance_to_next_driver(TRACK_POINTS, DRIVERS[1], DRIVERS)), True, "white"), (0, 26))
        # WIN.blit(FONT_1.render(str(DRIVERS[0].speed * 2 * 60), True, "white"), (0, 26))
        # WIN.blit(FONT_1.render(str(DRIVERS[-1].speed * 2 * 60), True, "white"), (0, 50))

        pg.display.flip()


simulation_interface("sc1", mgr_team.ready_drivers())