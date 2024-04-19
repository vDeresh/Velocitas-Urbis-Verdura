import json
from os import path
from typing import Any
from ..classes import Team, Driver

PATH1 = path.abspath(path.join("src", "data", "teams"))
PATH2 = path.abspath(path.join("src", "data", "drivers"))


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
        for driver in (drivers := driver_show()):
            for n in teams[team_name]['drivers']:
                if n == drivers[driver]['number']:
                    DRIVERS.append(Driver(Team(team_name, teams[team_name]), drivers[driver]['number'], drivers[driver]['skills']))

    return DRIVERS