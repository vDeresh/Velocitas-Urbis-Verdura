from ..config import *
from ..manager import track as mgr_track
from ..manager import team as mgr_team
from ..classes import Team, Driver, distance_to_next_driver
# from ..others import distance_to_next_driver


def simulation(track_name: str, DRIVERS: list[Driver]) -> None:
    TRACK_INFO = mgr_track.show()[track_name]['info']

    TRACK = mgr_track.show()[track_name]['track']
    TRACK_POINTS = mgr_track.convert_track_to_points(TRACK)
    TRACK_POINTS_SCALED = mgr_track.scale_track_points(TRACK_POINTS)

    PITLANE = mgr_track.show()[track_name]['pit-lane']
    PITLANE_POINTS = mgr_track.convert_track_to_points(PITLANE)
    PITLANE_POINTS_SCALED = mgr_track.scale_track_points(PITLANE_POINTS)

    # DRIVERS = DRIVERS[:2:]
    # DRIVERS = [DRIVERS[0]]
    # DRIVERS = [DRIVERS[0], DRIVERS[-1]]
    DRIVERS = DRIVERS[::2]

    # print(TRACK)
    # print(DRIVERS)
    # print()

    for n, driver in enumerate(DRIVERS):
        driver.set_pos(TRACK_POINTS[0][0] - 12 * TRACK_INFO['starting-direction'][0] * (n + 1), TRACK_POINTS[0][1] - 12 * TRACK_INFO['starting-direction'][1] * (n + 1))
        # driver.set_pos(TRACK_POINTS[0][0], TRACK_POINTS[0][1])
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
        pg.draw.aalines(WIN, "azure1", True, TRACK_POINTS_SCALED)
        pg.draw.aalines(WIN, "azure4", False, PITLANE_POINTS_SCALED)

        for driver in DRIVERS:
            driver.post_update()
            pg.draw.circle(WIN, driver.team.color, driver.pos / 2, 2)

        WIN.blit(FONT_1.render(str(int(clock.get_fps())), True, "white"), (0, 0))
        WIN.blit(FONT_1.render(str(LAP), True, "white"), (0, 26))
        # WIN.blit(FONT_1.render(str(distance_to_next_driver(TRACK_POINTS, DRIVERS[1], DRIVERS)), True, "white"), (0, 26))
        # WIN.blit(FONT_1.render(str(DRIVERS[0].speed * 2 * 60), True, "white"), (0, 26))
        # WIN.blit(FONT_1.render(str(DRIVERS[-1].speed * 2 * 60), True, "white"), (0, 50))

        pg.draw.rect(WIN, "red", (TRACK_POINTS_SCALED[0][0] - 1, TRACK_POINTS_SCALED[0][1] - 1, 4, 4), 2)
        pg.display.flip()

        DRIVERS.sort(key=lambda x: (x.lap, x.current_point, -x.pos.distance_to(x.next_point_xy), x.speed), reverse=True) # the bigger the better
        LAP = DRIVERS[0].lap


simulation("sc1", mgr_team.ready_drivers())