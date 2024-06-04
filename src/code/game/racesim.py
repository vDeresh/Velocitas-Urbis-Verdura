from ..config import *
from ..manager import main_mgr
from ..classes import Driver, Timer
# from ..others import calculate_pit_entry_point as init_others

from threading import Thread
# from multiprocessing import Process
# from time import perf_counter
from random import shuffle


def qualifications(shared, TRACK, TRACK_POINTS, TRACK_INFO, PITLANE, PITLANE_POINTS, DRIVERS: list[Driver]) -> list:
    clock = pg.Clock()

    shuffle(DRIVERS)

    while 1:
        clock.tick(60)

        for n, driver in enumerate(DRIVERS):
            driver.position = n + 1
            driver.qualifications(TRACK, TRACK_POINTS, PITLANE, PITLANE_POINTS, TRACK_INFO)

        DRIVERS.sort(key=lambda x: (x.quali_best_lap_time, x.number))
        shared["fps"] = clock.get_fps()

    return DRIVERS


def simulation(shared, TRACK, TRACK_POINTS, TRACK_INFO, PITLANE, PITLANE_POINTS, DRIVERS: list[Driver]) -> None:
    DRIVERS.sort(key=lambda x: (x.lap, x.current_point, -x.pos.distance_to(x.next_point_xy), x.speed), reverse=True)

    TIMERS = [Timer(_id, TRACK_INFO['timer-pos'][n]) for n, _id in enumerate(TRACK_INFO['timer-ids'])]

    ALL_LAPS = 1 # 200_000 // TRACK_INFO['length'] + 1

    _end_it_all_timer = 60 * 4

    clock = pg.Clock()
    while 1:
        clock.tick(60)

        prev_DRIVERS = DRIVERS
        for n, driver in enumerate(DRIVERS):
            driver.position = n + 1
            driver.update(TRACK, TRACK_POINTS, PITLANE, PITLANE_POINTS, TRACK_INFO, prev_DRIVERS)

            if driver.lap > ALL_LAPS:
                driver.slow = True
                continue

            if driver.current_point in TRACK_INFO['timer-ids'] \
            and any([driver.pos.distance_squared_to(tpos) < 2.25 for tpos in TRACK_INFO['timer-pos']]):
                for timer in TIMERS:
                    if timer.id == driver.current_point:
                        if timer.cached_driver != driver.number:
                            timer.cached_driver = driver.number
                            driver.time_difference = timer.time / 60
                            timer.time = 0
                        break

            if n == 0:
                driver.time_difference = 0

        for timer in TIMERS:
            timer.time += 1

        DRIVERS.sort(key=lambda x: (x.lap, x.current_point, -x.pos.distance_to(x.next_point_xy), x.speed), reverse=True) # the bigger the better

        if (_end_it_all_timer < 60 * 4) or all(d.lap > ALL_LAPS for d in DRIVERS):
            _end_it_all_timer -= 1

            if _end_it_all_timer <= 0:
                return

        shared["lap"] = DRIVERS[0].lap
        shared["fps"] = clock.get_fps()


def free_simulation_interface(racing_category_name: str, racing_class_name: str, track_name: str, DRIVERS: list[Driver]) -> None:
    SURF_MAIN = pg.Surface((WIN_W, WIN_H))
    IMG_RACE_UI = pg.image.load(os.path.join("src", "textures", "race_ui.png")).convert_alpha()

    main_mgr.init(racing_category_name, racing_class_name)

    # shuffle(DRIVERS)

    track_features = main_mgr.get_features(racing_category_name, racing_class_name, track_name)
    class_manifest = main_mgr.read_manifest(racing_category_name, racing_class_name)

    if isinstance(track_features, dict):
        ALL_TRACKS = main_mgr.track_show(track_name)

        TRACK_INFO = ALL_TRACKS[class_manifest['racing-type']]['info']
        TRACK      = ALL_TRACKS[class_manifest['racing-type']]['track']

        TRACK_POINTS = main_mgr.convert_track_to_points(TRACK)
        TRACK_POINTS_SCALED = main_mgr.scale_track_points(TRACK_POINTS, ALL_TRACKS['scale'])

        if track_features['pit-lane']:
            PITLANE = ALL_TRACKS[class_manifest['racing-type']]['pit-lane']
            PITLANE_POINTS = main_mgr.convert_track_to_points(PITLANE)
            PITLANE_POINTS_SCALED = main_mgr.scale_track_points(PITLANE_POINTS, ALL_TRACKS['scale'])
        else:
            PITLANE = PITLANE_POINTS = PITLANE_POINTS_SCALED = []
    else:
        raise ValueError(f"{racing_category_name}\\{racing_class_name} is not allowed on track `{track_name}`")


    TRACK_INFO['timer-ids'] = set(TRACK_INFO['timer-ids'])


    ALL_LAPS = 1 # 200_000 // TRACK_INFO['length'] + 1


    for n, driver in enumerate(DRIVERS):
        driver.init(TRACK, n + 1, 3)
        driver.set_pos(TRACK_POINTS[0][0] - 10 * TRACK_INFO['starting-direction'][0] * (n + 1), TRACK_POINTS[0][1] - 10 * TRACK_INFO['starting-direction'][1] * (n + 1))
    else:
        del n, driver


    drs_zones: list[list] = []
    _temp_drs_zone_now = False
    _temp_drs_zone_counter = -1

    for n, p in enumerate(TRACK):
        if "drs-start" in p[2]:
            drs_zones.append([])
            _temp_drs_zone_counter += 1

            _temp_drs_zone_now = True
        elif "drs-end" in p[2]:
            _temp_drs_zone_now = False

        if _temp_drs_zone_now:
            drs_zones[_temp_drs_zone_counter].append(tuple(p[0:2]))

    drs_zones_scaled = [main_mgr.scale_track_points(drs_zone_points, TRACK_INFO['scale']) for drs_zone_points in drs_zones]

    del drs_zones, _temp_drs_zone_now, _temp_drs_zone_counter, n, p


    # For showing other tracks in this place ----
    all_tracks = []
    all_tracks_points_scaled = []
    n = -1
    for t in ALL_TRACKS:
        if not t in ["formula", "rallycross"]: continue
        else: n += 1

        for p in ALL_TRACKS[t]['track']:
            if len(all_tracks) < n + 1:
                all_tracks.append([])
            all_tracks[n].append(p)
    else:
        for t in all_tracks:
            temp_all_tracks_scaled = []
            for p in t:
                temp_all_tracks_scaled.append(p[0 : 2])

            all_tracks_points_scaled.append(main_mgr.scale_track_points(temp_all_tracks_scaled, ALL_TRACKS['scale']))

        del n, t, p, temp_all_tracks_scaled, all_tracks
    # -------------------------------------------

    _current_surface_type = "asphalt"


    SURF_MONITOR   = pg.Surface(((860 - 20) * 2, (440 - 20) * 2), pg.SRCALPHA)
    SURF_TRACK     = pg.Surface((500, 500), pg.SRCALPHA)
    SURF_POSITIONS = pg.Surface((428, 500), pg.SRCALPHA)
    SURF_RACE_INFO = pg.Surface((500, 120), pg.SRCALPHA)


    SHARED = {
        "fps": 0,
        "lap": 0
    }

    _thread_simulation = Thread(target=simulation, name="simulation-thread", args=[SHARED, TRACK, TRACK_POINTS, TRACK_INFO, PITLANE, PITLANE_POINTS, DRIVERS], daemon=True)
    _thread_simulation.start()

    clock = pg.Clock()

    TIMER_S = 0

    while 1:
        if TIMER_S != 0 and not TIMER_S % 60:
            TIMER_S = 0
        else:
            TIMER_S += 1

        clock.tick(60)

        for e in pg.event.get():
            if e.type == pg.QUIT:
                pg.quit()
                exit()


        SURF_MAIN.fill(COLOR_BACKGROUND)
        SURF_MAIN.blit(IMG_RACE_UI, (0, 0))

        SURF_TRACK.fill((0, 0, 0, 0))
        SURF_RACE_INFO.fill((0, 0, 0, 0))


        for t in all_tracks_points_scaled: # Showing other (all) tracks
            # for n2, p in enumerate(t):
            #     if "dirt" in all_tracks[n1][n2][2]:
            #         _current_surface_type = "dirt"
            #     elif "asphalt" in all_tracks[n1][n2][2]:
            #         _current_surface_type = "asphalt"

            # if _current_surface_type == "dirt":
            #     pg.draw.aalines(WIN, "gray50", True, t)
            # else:
                pg.draw.aalines(SURF_TRACK, "gray16", True, t)


        if track_features['pit-lane']:
            pg.draw.aalines(SURF_TRACK, "azure4", False, PITLANE_POINTS_SCALED)

        # pg.draw.lines(WIN, "azure1", True, TRACK_POINTS_SCALED)
        for n, p in enumerate(TRACK_POINTS_SCALED):
            # pg.draw.aalines(WIN, "azure1", True, TRACK_POINTS_SCALED)

            if "dirt" in TRACK[n][2]:
                _current_surface_type = "dirt"
            elif "asphalt" in TRACK[n][2]:
                _current_surface_type = "asphalt"

            if n < len(TRACK_POINTS_SCALED) - 1:
                if _current_surface_type == "dirt":
                    pg.draw.aalines(SURF_TRACK, "orange", True, [p, TRACK_POINTS_SCALED[n + 1]])
                else:
                    pg.draw.aalines(SURF_TRACK, "azure1", True, [p, TRACK_POINTS_SCALED[n + 1]])
            else:
                if _current_surface_type == "dirt":
                    pg.draw.aalines(SURF_TRACK, "orange", True, [p, TRACK_POINTS_SCALED[0]])
                else:
                    pg.draw.aalines(SURF_TRACK, "azure1", True, [p, TRACK_POINTS_SCALED[0]])

        # pg.draw.lines(WIN, "lime", False, drs_zone_points_scaled)
        if track_features['drs']:
            for drs_zone_points_scaled in drs_zones_scaled:
                pg.draw.aalines(WIN, "lime", False, drs_zone_points_scaled)

        # pg.draw.rect(WIN, "red", (TRACK_POINTS_SCALED[0][0] - 1, TRACK_POINTS_SCALED[0][1] - 1, 3, 3), 2)
        pg.draw.circle(SURF_TRACK, "red", (TRACK_POINTS_SCALED[0]), 2)

        for driver in DRIVERS:
            if driver.tyre_type == 0:
                pg.draw.circle(SURF_TRACK, "#ff7a7a", driver.pos / 2 / ALL_TRACKS['scale'], 2)
            elif driver.tyre_type == 1:
                pg.draw.circle(SURF_TRACK, "#c61010", driver.pos / 2 / ALL_TRACKS['scale'], 2)
            elif driver.tyre_type == 2:
                pg.draw.circle(SURF_TRACK, "#ffcf24", driver.pos / 2 / ALL_TRACKS['scale'], 2)
            elif driver.tyre_type == 3:
                pg.draw.circle(SURF_TRACK, "#f2f2f2", driver.pos / 2 / ALL_TRACKS['scale'], 2)
            elif driver.tyre_type == 4:
                pg.draw.circle(SURF_TRACK, "#21ad46", driver.pos / 2 / ALL_TRACKS['scale'], 2)
            elif driver.tyre_type == 5:
                pg.draw.circle(SURF_TRACK, "#0050d1", driver.pos / 2 / ALL_TRACKS['scale'], 2)
            pg.draw.circle(SURF_TRACK, driver.team.color, driver.pos / 2 / ALL_TRACKS['scale'], 1)

        SURF_MAIN.blit(FONT_1.render(str(SHARED['fps']), True, "white"), (0, 0))


        # SURF_RACE_INFO -------------------------------------------------------------------------------------
        SURF_RACE_INFO.blit(FONT_2.render("Track", True, "azure"), (0, 0))
        SURF_RACE_INFO.blit(FONT_1.render(str(track_name), False, "azure3"), (80, 0))

        SURF_RACE_INFO.blit(FONT_2.render("Lap", True, "azure"), (0, 22))
        SURF_RACE_INFO.blit(FONT_1.render(str(SHARED['lap']) + "/" + str(ALL_LAPS), False, "azure3"), (80, 22))
        # ------------------------------------------------------------------------------------- SURF_RACE_INFO
        # WIN.blit(FONT_1.render(str(DRIVERS[1].speed * 2 * 60), True, "white"), (0, 26))


        # SURF_POSITIONS -------------------------------------------------------------------------------------
        if not TIMER_S % 10:
            SURF_POSITIONS.fill((0, 0, 0, 0))

            for n, d in enumerate(DRIVERS):
                _const_pos_name_x = 20 + FONT_1.render("00", True, "black").get_width()
                _const_pos_time_x = 428 - FONT_1.render("0.000", True, "black").get_width()
                _const_pos_team_x = _const_pos_time_x - 20 - FONT_2.render("XXX", True, "black").get_width()

                SURF_POSITIONS.blit(FONT_1.render(f"{d.number:02}",                                                  False, "azure4"), (0,  22 * n))
                SURF_POSITIONS.blit(FONT_2.render(f"{d.name[1] if len(d.name[1]) <= 17 else d.name[1][:15] + ".."}", True, "azure1"), (_const_pos_name_x, 22 * n))
                SURF_POSITIONS.blit(FONT_2.render(f"{d.team.name_abbreviation}",                                     True, "azure3"), (_const_pos_team_x, 22 * n))
                if d.lap <= ALL_LAPS:
                    SURF_POSITIONS.blit(FONT_1.render(f"{round(d.time_difference, 3) if d.time_difference > 0 else "-int-" if d.position == 1 else ""}", False, "azure3" if d.position == 1 else "azure4"), (_const_pos_time_x, 22 * n))
                else:
                    SURF_POSITIONS.blit(FONT_1.render("-fin-", False, "azure3"), (_const_pos_time_x, 22 * n))
        # ------------------------------------------------------------------------------------- SURF_POSITIONS


        SURF_MONITOR.fill((0, 0, 0, 0))
        SURF_MONITOR.blit(SURF_TRACK, (4, 336))
        SURF_MONITOR.blit(SURF_POSITIONS, (520, 336))
        SURF_MONITOR.blit(SURF_RACE_INFO, (4, 200))
        SURF_MAIN.blit(SURF_MONITOR, (100 + 20, 100 + 20))
        WIN.blit(SURF_MAIN, (0, 0))
        pg.display.flip()

        if not _thread_simulation.is_alive():
            fadeout = pg.Surface((WIN_W, WIN_H))
            fadeout.fill((0, 0, 0))

            for n in range(256):
                clock.tick(60 * 2)
                pg.event.pump()

                WIN.blit(SURF_MAIN, (0, 0))
                fadeout.set_alpha(n)
                WIN.blit(fadeout, (0, 0))

                pg.display.flip()

            return


def career_simulation_interface(racing_category_name: str, racing_class_name: str, track_name: str, DRIVERS: list[Driver], career_name: str) -> None:
    SURF_MAIN = pg.Surface((WIN_W, WIN_H))
    IMG_RACE_UI = pg.image.load(os.path.join("src", "textures", "race_ui.png")).convert_alpha()

    main_mgr.init(racing_category_name, racing_class_name)

    shuffle(DRIVERS)

    track_features = main_mgr.get_features(racing_category_name, racing_class_name, track_name)
    class_manifest = main_mgr.read_manifest(racing_category_name, racing_class_name)

    if isinstance(track_features, dict):
        TRACK_INFO = main_mgr.track_show(track_name)[class_manifest['racing-type']]['info']
        TRACK      = main_mgr.track_show(track_name)[class_manifest['racing-type']]['track']

        ALL_TRACKS = main_mgr.track_show(track_name)

        TRACK_POINTS = main_mgr.convert_track_to_points(TRACK)
        TRACK_POINTS_SCALED = main_mgr.scale_track_points(TRACK_POINTS, TRACK_INFO['scale'])

        if track_features['pit-lane']:
            PITLANE = main_mgr.track_show(track_name)[class_manifest['racing-type']]['pit-lane']
            PITLANE_POINTS = main_mgr.convert_track_to_points(PITLANE)
            PITLANE_POINTS_SCALED = main_mgr.scale_track_points(PITLANE_POINTS, TRACK_INFO['scale'])
        else:
            PITLANE = PITLANE_POINTS = PITLANE_POINTS_SCALED = []
    else:
        raise ValueError(f"{racing_category_name}\\{racing_class_name} is not allowed on track `{track_name}`")


    TRACK_INFO['timer-ids'] = set(TRACK_INFO['timer-ids'])


    for n, driver in enumerate(DRIVERS):
        driver.init(TRACK, n + 1, 3)
        driver.set_pos(TRACK_POINTS[0][0] - 10 * TRACK_INFO['starting-direction'][0] * (n + 1), TRACK_POINTS[0][1] - 10 * TRACK_INFO['starting-direction'][1] * (n + 1))
    else:
        del n, driver


    SHARED = {
        "fps": 0,
        "lap": 0
    }


    drs_zones: list[list] = []
    _temp_drs_zone_now = False
    _temp_drs_zone_counter = -1

    for n, p in enumerate(TRACK):
        if "drs-start" in p[2]:
            drs_zones.append([])
            _temp_drs_zone_counter += 1

            _temp_drs_zone_now = True
        elif "drs-end" in p[2]:
            _temp_drs_zone_now = False

        if _temp_drs_zone_now:
            drs_zones[_temp_drs_zone_counter].append(tuple(p[0:2]))

    drs_zones_scaled = [main_mgr.scale_track_points(drs_zone_points, TRACK_INFO['scale']) for drs_zone_points in drs_zones]

    del drs_zones, _temp_drs_zone_now, _temp_drs_zone_counter, n, p


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

            all_tracks_points_scaled.append(main_mgr.scale_track_points(temp_all_tracks_scaled, TRACK_INFO['scale']))

        del n, t, p, temp_all_tracks_scaled, all_tracks
    # -------------------------------------------

    _current_surface_type = "asphalt"


    SURF_MONITOR   = pg.Surface(((860 - 20) * 2, (440 - 20) * 2), pg.SRCALPHA)
    SURF_TRACK     = pg.Surface((500, 500), pg.SRCALPHA)
    SURF_POSITIONS = pg.Surface((428, 500), pg.SRCALPHA)
    SURF_RACE_INFO = pg.Surface((500, 120), pg.SRCALPHA)

    # SURF_TRACK.fill(COLOR_MONITOR)
    # SURF_POSITIONS.fill(COLOR_MONITOR)
    # SURF_RACE_INFO.fill(COLOR_MONITOR)

    _thread_simulation = Thread(target=simulation, name="simulation-thread", args=[SHARED, TRACK, TRACK_POINTS, TRACK_INFO, PITLANE, PITLANE_POINTS, DRIVERS], daemon=True)
    _thread_simulation.start()

    # _process_simulation = Process(target=simulation, name="simulation-process", args=[SHARED, TRACK, TRACK_POINTS, TRACK_INFO, PITLANE, PITLANE_POINTS, DRIVERS], daemon=True)
    # _process_simulation.start()

    clock = pg.Clock()

    TIMER_S = 0

    while 1:
        if TIMER_S != 0 and not TIMER_S % 60:
            TIMER_S = 0
        else:
            TIMER_S += 1

        clock.tick(60)

        for e in pg.event.get():
            if e.type == pg.QUIT:
                pg.quit()
                exit()


        SURF_MAIN.fill(COLOR_BACKGROUND)
        SURF_MAIN.blit(IMG_RACE_UI, (0, 0))

        SURF_TRACK.fill((0, 0, 0, 0))
        SURF_RACE_INFO.fill((0, 0, 0, 0))


        for t in all_tracks_points_scaled: # Showing other (all) tracks
            # for n2, p in enumerate(t):
            #     if "dirt" in all_tracks[n1][n2][2]:
            #         _current_surface_type = "dirt"
            #     elif "asphalt" in all_tracks[n1][n2][2]:
            #         _current_surface_type = "asphalt"

            # if _current_surface_type == "dirt":
            #     pg.draw.aalines(WIN, "gray50", True, t)
            # else:
                pg.draw.aalines(SURF_TRACK, "gray16", True, t)


        if track_features['pit-lane']:
            pg.draw.aalines(SURF_TRACK, "azure4", False, PITLANE_POINTS_SCALED)

        for n, p in enumerate(TRACK_POINTS_SCALED):

            if "dirt" in TRACK[n][2]:
                _current_surface_type = "dirt"
            elif "asphalt" in TRACK[n][2]:
                _current_surface_type = "asphalt"

            if n < len(TRACK_POINTS_SCALED) - 1:
                if _current_surface_type == "dirt":
                    pg.draw.aalines(SURF_TRACK, "orange", True, [p, TRACK_POINTS_SCALED[n + 1]])
                else:
                    pg.draw.aalines(SURF_TRACK, "azure1", True, [p, TRACK_POINTS_SCALED[n + 1]])
            else:
                if _current_surface_type == "dirt":
                    pg.draw.aalines(SURF_TRACK, "orange", True, [p, TRACK_POINTS_SCALED[0]])
                else:
                    pg.draw.aalines(SURF_TRACK, "azure1", True, [p, TRACK_POINTS_SCALED[0]])

        if track_features['drs']:
            for drs_zone_points_scaled in drs_zones_scaled:
                pg.draw.aalines(WIN, "lime", False, drs_zone_points_scaled)

        pg.draw.circle(SURF_TRACK, "red", (TRACK_POINTS_SCALED[0]), 2)

        for driver in DRIVERS:
            if driver.tyre_type == 0:
                pg.draw.circle(SURF_TRACK, "#ff7a7a", driver.pos / 2 / TRACK_INFO['scale'], 2)
            elif driver.tyre_type == 1:
                pg.draw.circle(SURF_TRACK, "#c61010", driver.pos / 2 / TRACK_INFO['scale'], 2)
            elif driver.tyre_type == 2:
                pg.draw.circle(SURF_TRACK, "#ffcf24", driver.pos / 2 / TRACK_INFO['scale'], 2)
            elif driver.tyre_type == 3:
                pg.draw.circle(SURF_TRACK, "#f2f2f2", driver.pos / 2 / TRACK_INFO['scale'], 2)
            elif driver.tyre_type == 4:
                pg.draw.circle(SURF_TRACK, "#21ad46", driver.pos / 2 / TRACK_INFO['scale'], 2)
            elif driver.tyre_type == 5:
                pg.draw.circle(SURF_TRACK, "#0050d1", driver.pos / 2 / TRACK_INFO['scale'], 2)
            pg.draw.circle(SURF_TRACK, driver.team.color, driver.pos / 2 / TRACK_INFO['scale'], 1)

        SURF_MAIN.blit(FONT_1.render(str(SHARED['fps']), True, "white"), (0, 0))


        # SURF_RACE_INFO -------------------------------------------------------------------------------------
        SURF_RACE_INFO.blit(FONT_2.render("Track", True, "azure"), (0, 0))
        SURF_RACE_INFO.blit(FONT_1.render(str(track_name), False, "azure3"), (80, 0))

        SURF_RACE_INFO.blit(FONT_2.render("Lap", True, "azure"), (0, 22))
        SURF_RACE_INFO.blit(FONT_1.render(str(SHARED['lap']), False, "azure3"), (80, 22))
        # ------------------------------------------------------------------------------------- SURF_RACE_INFO


        # SURF_POSITIONS -------------------------------------------------------------------------------------
        if not TIMER_S % 10:
            SURF_POSITIONS.fill((0, 0, 0, 0))

            for n, d in enumerate(DRIVERS):
                _const_pos_name_x = 20 + FONT_1.render("00", True, "black").get_width()
                _const_pos_time_x = 428 - FONT_1.render("0.000", True, "black").get_width()
                _const_pos_team_x = _const_pos_time_x - 20 - FONT_2.render("XXX", True, "black").get_width()

                SURF_POSITIONS.blit(FONT_1.render(f"{d.number:02}",                                                  False, "azure4"), (0,  22 * n))
                SURF_POSITIONS.blit(FONT_2.render(f"{d.name[1] if len(d.name[1]) <= 17 else d.name[1][:15] + ".."}", True, "azure1"), (_const_pos_name_x, 22 * n))
                SURF_POSITIONS.blit(FONT_2.render(f"{d.team.name_abbreviation}",                                     True, "azure3"), (_const_pos_team_x, 22 * n))
                SURF_POSITIONS.blit(FONT_1.render(f"{round(d.time_difference, 3) if d.time_difference > 0 else "-int-" if d.position == 1 else ""}", False, "azure3" if d.position == 1 else "azure4"), (_const_pos_time_x, 22 * n))
        # ------------------------------------------------------------------------------------- SURF_POSITIONS

        SURF_MONITOR.fill((0, 0, 0, 0))
        SURF_MONITOR.blit(SURF_TRACK, (4, 336))
        SURF_MONITOR.blit(SURF_POSITIONS, (520, 336))
        SURF_MONITOR.blit(SURF_RACE_INFO, (4, 200))
        SURF_MAIN.blit(SURF_MONITOR, (100 + 20, 100 + 20))
        WIN.blit(SURF_MAIN, (0, 0))
        pg.display.flip()



# def simulation_no_racing(shared, TRACK, TRACK_POINTS, TRACK_INFO, PITLANE, PITLANE_POINTS, DRIVERS: list[Driver]) -> None:
#     clock = pg.Clock()

#     DRIVERS.sort(key=lambda x: (x.lap, x.current_point, -x.pos.distance_to(x.next_point_xy), x.speed), reverse=True)

#     while 1:
#         clock.tick(60)

#         for n, driver in enumerate(DRIVERS):
#             driver.position = n + 1
#             driver.update(TRACK, TRACK_POINTS, PITLANE, PITLANE_POINTS, TRACK_INFO, [])

#         DRIVERS.sort(key=lambda x: (x.lap, x.current_point, -x.pos.distance_to(x.next_point_xy), x.speed), reverse=True) # the bigger the better
#         shared["lap"] = DRIVERS[0].lap
#         shared["fps"] = clock.get_fps()