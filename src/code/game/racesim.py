from ..config import *
from ..manager import main_mgr
from ..classes import Team, Driver, Timer
# from ..others import calculate_pit_entry_point as init_others

from threading import Thread
from time import perf_counter
from random import shuffle


def simulation(shared, TRACK, TRACK_POINTS, TRACK_INFO, PITLANE, PITLANE_POINTS, DRIVERS: list[Driver]) -> None:
    clock = pg.Clock()

    TIMERS = [Timer(_id, TRACK_INFO['timer-pos'][n]) for n, _id in enumerate(TRACK_INFO['timer-ids'])]

    DRIVERS.sort(key=lambda x: (x.lap, x.current_point, -x.pos.distance_to(x.next_point_xy), x.speed), reverse=True)

    while 1:
        clock.tick(60)

        prev_DRIVERS = DRIVERS
        for n, driver in enumerate(DRIVERS):
            driver.position = n + 1
            driver.update(TRACK, TRACK_POINTS, PITLANE, PITLANE_POINTS, TRACK_INFO, prev_DRIVERS)

            if driver.current_point in TRACK_INFO['timer-ids'] \
            and any([driver.pos.distance_squared_to(tpos) < 2.25 for tpos in TRACK_INFO['timer-pos']]):
                for timer in TIMERS:
                    if timer.id == driver.current_point:
                        if timer.cached_driver != driver.number:
                            timer.cached_driver = driver.number
                            driver.time_difference = perf_counter() - timer.time
                            timer.time = perf_counter()
                        break

            if n == 0:
                driver.time_difference = 0

        DRIVERS.sort(key=lambda x: (x.lap, x.current_point, -x.pos.distance_to(x.next_point_xy), x.speed), reverse=True) # the bigger the better
        shared["lap"] = DRIVERS[0].lap
        shared["fps"] = clock.get_fps()


def simulation_interface(track_name: str, DRIVERS: list[Driver]) -> None:
    DRIVERS = DRIVERS[::2]

    shuffle(DRIVERS)

    for driver in DRIVERS[::2]:
        driver.call_stack.append({"type": "pit", "tyre": 2})
    else:
        del driver

    TRACK_INFO = main_mgr.track_show()[track_name]['info']

    TRACK = main_mgr.track_show()[track_name]['track']
    PITLANE = main_mgr.track_show()[track_name]['pit-lane']

    TRACK_POINTS = main_mgr.convert_track_to_points(TRACK)
    PITLANE_POINTS = main_mgr.convert_track_to_points(PITLANE)

    TRACK_POINTS_SCALED = main_mgr.scale_track_points(TRACK_POINTS)
    PITLANE_POINTS_SCALED = main_mgr.scale_track_points(PITLANE_POINTS)


    TRACK_INFO['timer-ids'] = set(TRACK_INFO['timer-ids'])


    for n, driver in enumerate(DRIVERS):
        driver.init(TRACK, n + 1, 3)
        driver.set_pos(TRACK_POINTS[0][0] - 8 * TRACK_INFO['starting-direction'][0] * (n + 1), TRACK_POINTS[0][1] - 8 * TRACK_INFO['starting-direction'][1] * (n + 1))
        # driver.set_pos(TRACK_POINTS[0][0], TRACK_POINTS[0][1])
    else:
        del n, driver


    SHARED = {
        "fps": 0,
        "lap": 0
    }


    drs_zone_points = []
    for n, p in enumerate(TRACK):
        if "drs-start" in p[2]:
            for p2 in TRACK[n:] + TRACK[:n]:
                drs_zone_points.append(tuple(p2[0 : 2]))
                if "drs-end" in p2[2]:
                    del n, p, p2
                    break

    drs_zone_points_scaled = main_mgr.scale_track_points(drs_zone_points)
    del drs_zone_points


    _thread_simulation = Thread(target=simulation, name="simulation-thread", args=[SHARED, TRACK, TRACK_POINTS, TRACK_INFO, PITLANE, PITLANE_POINTS, DRIVERS], daemon=True)
    _thread_simulation.start()

    while 1:
        for e in pg.event.get():
            if e.type == pg.QUIT:
                pg.quit()
                exit()

        WIN.fill("black")
        pg.draw.aalines(WIN, "azure4", False, PITLANE_POINTS_SCALED)

        # pg.draw.lines(WIN, "azure1", True, TRACK_POINTS_SCALED)
        pg.draw.aalines(WIN, "azure1", True, TRACK_POINTS_SCALED)

        # pg.draw.lines(WIN, "lime", False, drs_zone_points_scaled)
        pg.draw.aalines(WIN, "lime", False, drs_zone_points_scaled)

        pg.draw.rect(WIN, "red", (TRACK_POINTS_SCALED[0][0] - 1, TRACK_POINTS_SCALED[0][1] - 1, 3, 3), 2)

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
        WIN.blit(FONT_1.render(str(DRIVERS[1].speed * 2 * 60), True, "white"), (0, 26))

        # for n, d in enumerate(DRIVERS):
        #     WIN.blit(FONT_1.render(str(round(d.time_difference, 3)), True, "white"), (0, 26 * (n + 1)))

        pg.display.flip()


simulation_interface("sc1", main_mgr.ready_drivers())