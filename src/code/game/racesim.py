from ..config import *
from ..manager import main_mgr
from ..classes import Team, Driver, Timer
# from ..others import calculate_pit_entry_point as init_others

from threading import Thread
from time import perf_counter
from random import shuffle


def qualifications(shared, TRACK, TRACK_POINTS, TRACK_INFO, PITLANE, PITLANE_POINTS, DRIVERS: list[Driver]) -> list:
    clock = pg.Clock()

    shuffle(DRIVERS)

    while 1:
        clock.tick(60)

        for n, driver in enumerate(DRIVERS):
            driver.position = n + 1
            driver.qualifications(TRACK, TRACK_POINTS, PITLANE, PITLANE_POINTS, TRACK_INFO)

        DRIVERS.sort(key=lambda x: x.quali_best_lap_time)
        shared["fps"] = clock.get_fps()

    return DRIVERS


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


def simulation_interface(racing_category_name: str, racing_class_name: str, track_name: str, DRIVERS: list[Driver]) -> None:
    main_mgr.init(racing_category_name, racing_class_name)

    # DRIVERS = DRIVERS[:len(DRIVERS) // 2]
    shuffle(DRIVERS)

    # for driver in DRIVERS[::2]:
    #     driver.call_stack.append({"type": "pit", "tyre": 2})
    # else:
    #     del driver

    track_features = main_mgr.get_features(racing_category_name, racing_class_name, track_name)
    class_manifest = main_mgr.read_manifest(racing_category_name, racing_class_name)

    if isinstance(track_features, dict):
        TRACK_INFO = main_mgr.track_show(track_name)[class_manifest['racing-type']]['info']
        TRACK      = main_mgr.track_show(track_name)[class_manifest['racing-type']]['track']

        ALL_TRACKS = main_mgr.track_show(track_name)

        TRACK_POINTS = main_mgr.convert_track_to_points(TRACK)
        TRACK_POINTS_SCALED = main_mgr.scale_track_points(TRACK_POINTS)

        if track_features['pit-lane']:
            PITLANE = main_mgr.track_show(track_name)[class_manifest['racing-type']]['pit-lane']
            PITLANE_POINTS = main_mgr.convert_track_to_points(PITLANE)
            PITLANE_POINTS_SCALED = main_mgr.scale_track_points(PITLANE_POINTS)
        else:
            PITLANE = PITLANE_POINTS = PITLANE_POINTS_SCALED = []
    else:
        raise ValueError(f"{racing_category_name}\\{racing_class_name} is not allowed on track `{track_name}`")


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


    # For showing other tracks in this place ----
    all_tracks = [[]]
    all_tracks_points_scaled = []
    for n, t in enumerate(ALL_TRACKS):
        n -= 3
        if n < 0: continue
        for p in ALL_TRACKS[t]['track']:
            if len(all_tracks) < n + 1:
                all_tracks.append([])
            all_tracks[n].append(p)
    else:
        for t in all_tracks:
            temp_all_tracks_scaled = []
            for p in t:
                temp_all_tracks_scaled.append(p[0 : 2])

            all_tracks_points_scaled.append(main_mgr.scale_track_points(temp_all_tracks_scaled))

        del n, t, p, temp_all_tracks_scaled, all_tracks
    # -------------------------------------------

    _thread_simulation = Thread(target=simulation, name="simulation-thread", args=[SHARED, TRACK, TRACK_POINTS, TRACK_INFO, PITLANE, PITLANE_POINTS, DRIVERS], daemon=True)
    _thread_simulation.start()

    _current_surface_type = "asphalt"

    while 1:
        for e in pg.event.get():
            if e.type == pg.QUIT:
                pg.quit()
                exit()

        WIN.fill("black")

        for t in all_tracks_points_scaled: # Showing other (all) tracks
            # for n2, p in enumerate(t):
            #     if "dirt" in all_tracks[n1][n2][2]:
            #         _current_surface_type = "dirt"
            #     elif "asphalt" in all_tracks[n1][n2][2]:
            #         _current_surface_type = "asphalt"

            # if _current_surface_type == "dirt":
            #     pg.draw.aalines(WIN, "gray50", True, t)
            # else:
                pg.draw.aalines(WIN, "gray16", True, t)


        if track_features['pit-lane']:
            pg.draw.aalines(WIN, "azure4", False, PITLANE_POINTS_SCALED)

        # pg.draw.lines(WIN, "azure1", True, TRACK_POINTS_SCALED)
        for n, p in enumerate(TRACK_POINTS_SCALED):
            # pg.draw.aalines(WIN, "azure1", True, TRACK_POINTS_SCALED)

            if "dirt" in TRACK[n][2]:
                _current_surface_type = "dirt"
            elif "asphalt" in TRACK[n][2]:
                _current_surface_type = "asphalt"

            if n < len(TRACK_POINTS_SCALED) - 1:
                if _current_surface_type == "dirt":
                    pg.draw.aalines(WIN, "orange", True, [p, TRACK_POINTS_SCALED[n + 1]])
                else:
                    pg.draw.aalines(WIN, "azure1", True, [p, TRACK_POINTS_SCALED[n + 1]])
            else:
                if _current_surface_type == "dirt":
                    pg.draw.aalines(WIN, "orange", True, [p, TRACK_POINTS_SCALED[0]])
                else:
                    pg.draw.aalines(WIN, "azure1", True, [p, TRACK_POINTS_SCALED[0]])

        # pg.draw.lines(WIN, "lime", False, drs_zone_points_scaled)
        if track_features['drs']:
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
        WIN.blit(FONT_1.render(str(SHARED['lap']), True, "white"), (0, 26))
        # WIN.blit(FONT_1.render(str(DRIVERS[1].speed * 2 * 60), True, "white"), (0, 26))

        # for n, d in enumerate(DRIVERS):
        #     WIN.blit(FONT_1.render(str(round(d.time_difference, 3)), True, "white"), (0, 26 * (n + 1)))

        pg.display.flip()



def simulation_no_racing(shared, TRACK, TRACK_POINTS, TRACK_INFO, PITLANE, PITLANE_POINTS, DRIVERS: list[Driver]) -> None:
    clock = pg.Clock()

    DRIVERS.sort(key=lambda x: (x.lap, x.current_point, -x.pos.distance_to(x.next_point_xy), x.speed), reverse=True)

    while 1:
        clock.tick(60)

        for n, driver in enumerate(DRIVERS):
            driver.position = n + 1
            driver.update(TRACK, TRACK_POINTS, PITLANE, PITLANE_POINTS, TRACK_INFO, [])

        DRIVERS.sort(key=lambda x: (x.lap, x.current_point, -x.pos.distance_to(x.next_point_xy), x.speed), reverse=True) # the bigger the better
        shared["lap"] = DRIVERS[0].lap
        shared["fps"] = clock.get_fps()