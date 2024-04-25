import json
from os import path
from typing import Any
from ..classes import Team, Driver

TOOLSPATH = path.abspath(path.join("tools", "simulator"))
if not path.exists(TOOLSPATH):
    TOOLSPATH = path.abspath("")

PATH1 = path.join(TOOLSPATH, "src", "data", "teams")
PATH2 = path.join(TOOLSPATH, "src", "data", "drivers")


def team_write(info: str, value: Any) -> None:
    with open(PATH1, "r") as file:
        data = json.load(file)

    data[info] = value

    with open(PATH1, "w") as file:
        json.dump(data, file, indent=4)


def team_show() -> dict:
    with open(PATH1, "r") as file:
        return json.load(file)


def driver_write(info: str, value: Any) -> None:
    with open(PATH2, "r") as file:
        data = json.load(file)

    data[info] = value

    with open(PATH2, "w") as file:
        json.dump(data, file, indent=4)


def driver_show() -> dict:
    with open(PATH2, "r") as file:
        return json.load(file)



def ready_drivers() -> list[Driver]:
    DRIVERS: list[Driver] = []

    for team_name in (teams := team_show()):
        for driver_name in (drivers := driver_show()):
            for n in teams[team_name]['drivers']:
                if n == drivers[driver_name]['number']:
                    DRIVERS.append(Driver(driver_name, Team(team_name, teams[team_name]), drivers[driver_name]['number'], drivers[driver_name]['skills']))

    return DRIVERS

def ready_equal_drivers() -> list[Driver]:
    DRIVERS: list[Driver] = []

    for team_name in (teams := {
                                "Team 01": {"id":  1, "drivers": [ 1,  2], "color": "#faafff", "name-abbreviation": "T01", "car-stats": {"mass": 700, "drag": 1.2, "downforce": 1}},
                                "Team 02": {"id":  2, "drivers": [ 3,  4], "color": "#0123ff", "name-abbreviation": "T02", "car-stats": {"mass": 700, "drag": 1.2, "downforce": 1}},
                                "Team 03": {"id":  3, "drivers": [ 5,  6], "color": "#4400bb", "name-abbreviation": "T03", "car-stats": {"mass": 700, "drag": 1.2, "downforce": 1}},
                                "Team 04": {"id":  4, "drivers": [ 7,  8], "color": "#dddddd", "name-abbreviation": "T04", "car-stats": {"mass": 700, "drag": 1.2, "downforce": 1}},
                                "Team 05": {"id":  5, "drivers": [ 9, 10], "color": "#fafb00", "name-abbreviation": "T05", "car-stats": {"mass": 700, "drag": 1.2, "downforce": 1}},
                                "Team 06": {"id":  6, "drivers": [11, 12], "color": "#fafafa", "name-abbreviation": "T06", "car-stats": {"mass": 700, "drag": 1.2, "downforce": 1}},
                                "Team 07": {"id":  7, "drivers": [13, 14], "color": "#afafaf", "name-abbreviation": "T07", "car-stats": {"mass": 700, "drag": 1.2, "downforce": 1}},
                                "Team 08": {"id":  8, "drivers": [15, 16], "color": "#5c6c7c", "name-abbreviation": "T08", "car-stats": {"mass": 700, "drag": 1.2, "downforce": 1}},
                                "Team 09": {"id":  9, "drivers": [17, 18], "color": "#1fff00", "name-abbreviation": "T09", "car-stats": {"mass": 700, "drag": 1.2, "downforce": 1}},
                                "Team 10": {"id": 10, "drivers": [19, 20], "color": "#ff8888", "name-abbreviation": "T10", "car-stats": {"mass": 700, "drag": 1.2, "downforce": 1}}
    }):
        for driver_name in (drivers := {
                                        "Driver 01": {"number":  1, "skills": {"attack": 0.2, "defence": 0.2, "breaking": 2, "reaction-time-multiplier": 1}},
                                        "Driver 02": {"number":  2, "skills": {"attack": 0.2, "defence": 0.2, "breaking": 2, "reaction-time-multiplier": 1}},
                                        "Driver 03": {"number":  3, "skills": {"attack": 0.2, "defence": 0.2, "breaking": 2, "reaction-time-multiplier": 1}},
                                        "Driver 04": {"number":  4, "skills": {"attack": 0.2, "defence": 0.2, "breaking": 2, "reaction-time-multiplier": 1}},
                                        "Driver 05": {"number":  5, "skills": {"attack": 0.2, "defence": 0.2, "breaking": 2, "reaction-time-multiplier": 1}},
                                        "Driver 06": {"number":  6, "skills": {"attack": 0.2, "defence": 0.2, "breaking": 2, "reaction-time-multiplier": 1}},
                                        "Driver 07": {"number":  7, "skills": {"attack": 0.2, "defence": 0.2, "breaking": 2, "reaction-time-multiplier": 1}},
                                        "Driver 08": {"number":  8, "skills": {"attack": 0.2, "defence": 0.2, "breaking": 2, "reaction-time-multiplier": 1}},
                                        "Driver 09": {"number":  9, "skills": {"attack": 0.2, "defence": 0.2, "breaking": 2, "reaction-time-multiplier": 1}},
                                        "Driver 10": {"number": 10, "skills": {"attack": 0.2, "defence": 0.2, "breaking": 2, "reaction-time-multiplier": 1}},
                                        "Driver 11": {"number": 11, "skills": {"attack": 0.2, "defence": 0.2, "breaking": 2, "reaction-time-multiplier": 1}},
                                        "Driver 12": {"number": 12, "skills": {"attack": 0.2, "defence": 0.2, "breaking": 2, "reaction-time-multiplier": 1}},
                                        "Driver 13": {"number": 13, "skills": {"attack": 0.2, "defence": 0.2, "breaking": 2, "reaction-time-multiplier": 1}},
                                        "Driver 14": {"number": 14, "skills": {"attack": 0.2, "defence": 0.2, "breaking": 2, "reaction-time-multiplier": 1}},
                                        "Driver 15": {"number": 15, "skills": {"attack": 0.2, "defence": 0.2, "breaking": 2, "reaction-time-multiplier": 1}},
                                        "Driver 16": {"number": 16, "skills": {"attack": 0.2, "defence": 0.2, "breaking": 2, "reaction-time-multiplier": 1}},
                                        "Driver 17": {"number": 17, "skills": {"attack": 0.2, "defence": 0.2, "breaking": 2, "reaction-time-multiplier": 1}},
                                        "Driver 18": {"number": 18, "skills": {"attack": 0.2, "defence": 0.2, "breaking": 2, "reaction-time-multiplier": 1}},
                                        "Driver 19": {"number": 19, "skills": {"attack": 0.2, "defence": 0.2, "breaking": 2, "reaction-time-multiplier": 1}},
                                        "Driver 20": {"number": 20, "skills": {"attack": 0.2, "defence": 0.2, "breaking": 2, "reaction-time-multiplier": 1}}
        }):
            for n in teams[team_name]['drivers']:
                if n == drivers[driver_name]['number']:
                    DRIVERS.append(Driver(driver_name, Team(team_name, teams[team_name]), drivers[driver_name]['number'], drivers[driver_name]['skills']))

    return DRIVERS