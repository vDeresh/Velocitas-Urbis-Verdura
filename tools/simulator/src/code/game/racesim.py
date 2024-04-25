from ..config import pg
from ..classes import Driver


def simulation(_fps: float, _update_in_realtime: bool, shared, TRACK, TRACK_POINTS, TRACK_INFO, PITLANE, PITLANE_POINTS, DRIVERS: list[Driver]) -> None:
    prev_lap: int
    _longest_name_length = len(max(DRIVERS, key=lambda x: len(x.name)).name)

    clock = pg.Clock()
    while 1:
        prev_lap = DRIVERS[0].lap
        clock.tick(_fps)

        prev_DRIVERS = DRIVERS.copy()
        for n, driver in enumerate(DRIVERS):
            driver.position = n + 1
            driver.update(TRACK, TRACK_POINTS, PITLANE, PITLANE_POINTS, TRACK_INFO, prev_DRIVERS)

        DRIVERS.sort(key=lambda x: (x.lap, x.current_point, -x.pos.distance_to(x.next_point_xy), x.speed), reverse=True)

        shared["lap"] = DRIVERS[0].lap
        shared["fps"] = clock.get_fps()


        if _update_in_realtime or prev_lap != DRIVERS[0].lap:
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