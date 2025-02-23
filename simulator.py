import sys
import pygame as pg
import os
from math import isinf


print(os.path.abspath(""))
os.chdir(os.path.abspath(""))


# _equal_drivers       = "--eq"  in sys.argv
_same_starting_point = "-ssp" in sys.argv
_show_track_data     = "-td"  in sys.argv
# _update_in_realtime  = "-uir" in sys.argv # for simulation
_racing_allowed      = "-ra"  in sys.argv
# _console_only        = "-co"  in sys.argv
_half_of_the_grid    = "-h"   in sys.argv
_shuffle_grid        = "-sg"  in sys.argv
_one_driver          = "-od"  in sys.argv
_tires               = 3
# _laps                = None
# _fps                 = 0 # for simulation
# _pit                 = False

# for np, p in enumerate(sys.argv):
#     if p == "--fps":
#         _fps = int(sys.argv[np + 1])
#         break

# for np, p in enumerate(sys.argv):
#     if p == "--pit":
#         _pit = int(sys.argv[np + 1])
#         break

# for np, p in enumerate(sys.argv):
#     if p == "--laps":
#         _laps = int(sys.argv[np + 1])
#         break

for np, p in enumerate(sys.argv):
    if p == "-t":
        _tires = int(sys.argv[np + 1])
        break
else:
    del np, p


from src.code.game.racesim import simulation, qualifications
from src.code.manager import main_mgr
from src.code.classes import Driver
# from src.code.config  import FONT_2, WIN

from threading import Thread
from random import shuffle


pg.quit()
pg.display.init()
pg.font.init()

WIN = pg.display.set_mode((500, 500), pg.SCALED)
FONT = pg.sysfont.SysFont("console", 16)


def simulation_interface(racing_category_name: str, racing_class_name: str, track_name: str, DRIVERS: list[Driver]) -> None:
    main_mgr.init(racing_category_name, racing_class_name)

    # DRIVERS = DRIVERS[:len(DRIVERS) // 2]

    if _half_of_the_grid:
        DRIVERS = DRIVERS[::2]

    if _one_driver:
        DRIVERS = [DRIVERS[0]]

    if _shuffle_grid:
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
        TRACK_POINTS_SCALED = main_mgr.scale_track_points(TRACK_POINTS, ALL_TRACKS['scale'])

        if track_features['pit-lane']:
            PITLANE = main_mgr.track_show(track_name)[class_manifest['racing-type']]['pit-lane']
            PITLANE_POINTS = main_mgr.convert_track_to_points(PITLANE)
            PITLANE_POINTS_SCALED = main_mgr.scale_track_points(PITLANE_POINTS, ALL_TRACKS['scale'])
        else:
            PITLANE = PITLANE_POINTS = PITLANE_POINTS_SCALED = []
    else:
        raise ValueError(f"{racing_category_name}\\{racing_class_name} is not allowed on track `{track_name}`")


    TRACK_INFO['timer-ids'] = set(TRACK_INFO['timer-ids'])


    _temp_reversed_track_list = list(range(len(TRACK_POINTS)).__reversed__())
    _temp_reversed_track_list.insert(0, 0)
    _temp_reversed_track_list.pop()

    for n1, driver in enumerate(DRIVERS):
        driver.init(TRACK, n1 + 1, _tires)
        if _same_starting_point:
            driver.set_pos(TRACK_POINTS[0][0], TRACK_POINTS[0][1])
        else:
            _temp_distance = 0
            for n2 in _temp_reversed_track_list:
                _temp_distance += pg.Vector2(TRACK_POINTS[n2]).distance_to(TRACK_POINTS[n2 - 1])

                if 10 * (n1 + 1) < _temp_distance:

                    _temp_starting_pos = (_temp_distance - 10 * (n1 + 1)) * (pg.Vector2(TRACK_POINTS[n2]) - pg.Vector2(TRACK_POINTS[n2 - 1])).normalize() + TRACK_POINTS[n2 - 1]
                    driver.set_pos(_temp_starting_pos.x, _temp_starting_pos.y)
                    driver.current_point = n2

                    _temp_distance = 0
                    break
    else:
        del n1, driver, _temp_distance
    del _temp_reversed_track_list


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

    drs_zones_scaled = [main_mgr.scale_track_points(drs_zone_points, ALL_TRACKS['scale']) for drs_zone_points in drs_zones]

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

    if _racing_allowed:
        _thread_simulation = Thread(target=simulation, name="simulation-thread", args=[SHARED, TRACK, TRACK_POINTS, TRACK_INFO, PITLANE, PITLANE_POINTS, DRIVERS], daemon=True)
        _thread_simulation.start()
    else:
        _thread_simulation = Thread(target=qualifications, name="simulation-thread (quali)", args=[SHARED, TRACK, TRACK_POINTS, TRACK_INFO, PITLANE, PITLANE_POINTS, DRIVERS], daemon=True)
        _thread_simulation.start()

    _current_surface_type = "asphalt"

    while 1:
        for e in pg.event.get():
            if e.type == pg.QUIT:
                pg.quit()
                exit()

        WIN.fill("black")

        for t in all_tracks_points_scaled: # Showing other (all) tracks
            pg.draw.aalines(WIN, "gray16", True, t)


        if track_features['pit-lane']: # drawing pitlane
            pg.draw.aalines(WIN, "azure4", False, PITLANE_POINTS_SCALED)

        for n, p in enumerate(TRACK_POINTS_SCALED): # drawing racetrack
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

        if track_features['drs']: # drawing drs zone
            for drs_zone in drs_zones_scaled:
                pg.draw.aalines(WIN, "lime", False, drs_zone)

        pg.draw.rect(WIN, "red", (TRACK_POINTS_SCALED[0][0] - 1, TRACK_POINTS_SCALED[0][1] - 1, 3, 3), 2) # drawing start


        if _show_track_data:
            for p in TRACK_POINTS_SCALED: # drawing track points
                pg.draw.circle(WIN, "darkred", p, 1)


        for driver in DRIVERS: # drawing drivers
            match driver.tyre_type:
                case 0:
                    pg.draw.circle(WIN, "#ff7a7a", driver.pos / 2 / ALL_TRACKS['scale'], 2)
                case 1:
                    pg.draw.circle(WIN, "#c61010", driver.pos / 2 / ALL_TRACKS['scale'], 2)
                case 2:
                    pg.draw.circle(WIN, "#ffcf24", driver.pos / 2 / ALL_TRACKS['scale'], 2)
                case 3:
                    pg.draw.circle(WIN, "#f2f2f2", driver.pos / 2 / ALL_TRACKS['scale'], 2)
                case 4:
                    pg.draw.circle(WIN, "#21ad46", driver.pos / 2 / ALL_TRACKS['scale'], 2)
                case 5:
                    pg.draw.circle(WIN, "#0050d1", driver.pos / 2 / ALL_TRACKS['scale'], 2)
            pg.draw.circle(WIN, driver.team.color, driver.pos / 2 / ALL_TRACKS['scale'], 1)


        WIN.blit(FONT.render(str(SHARED['fps']), True, "white"), (0, 0))

        if _racing_allowed:
            for n, d in enumerate(DRIVERS):
                WIN.blit(FONT.render(f"{d.number:02} {d.full_name} > {round(d.time_difference, 3)}", True, "white"), (0, 16 * (n + 1)))
        else:
            for n, d in enumerate(DRIVERS):
                if isinf(d.quali_best_lap_time):
                    WIN.blit(FONT.render(f"{d.number:02} > NO TIME SET", True, "white"), (0, 16 * (n + 1)))
                else:
                    # min_sec = divmod(d.quali_best_lap_time, 3600)
                    # m, s = int(min_sec[0]), min_sec[1]
                    # sec_msec = divmod(s, 60)
                    # s, ms = int(sec_msec[0]), sec_msec[1]

                    m, s, ms = int(d.quali_best_lap_time // 3600), int(d.quali_best_lap_time % 3600 // 60), round(d.quali_best_lap_time % 3600 % 60, 3)
                    if ms < 10:
                        WIN.blit(FONT.render(f"{d.number:02} > {m:02}:{s:02}.{str(ms).zfill(2)}", True, "white"), (0, 16 * (n + 1)))
                    else:
                        WIN.blit(FONT.render(f"{d.number:02} > {m:02}:{s:02}.{ms:0<2}", True, "white"), (0, 16 * (n + 1)))

        # self.quali_lap_time
        pg.display.flip()


# _racing_category_name = "Aper"
# _racing_class_name = "Aper 1"
_racing_category_name = "Volo"
_racing_class_name = "CAT-B"
_race_track_name = sys.argv[1] if (len(sys.argv) > 1) and not (sys.argv[1] in ["-ssp", "-td", "-ra", "-h", "-sg", "-od", "-t"]) else "mt5t"

simulation_interface(_racing_category_name, _racing_class_name, _race_track_name, main_mgr.ready_drivers(_racing_category_name, _racing_class_name))



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