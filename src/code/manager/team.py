import json
from os import path
from ..classes import Driver, Team


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