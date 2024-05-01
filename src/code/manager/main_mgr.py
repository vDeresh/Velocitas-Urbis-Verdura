import json
import os
from typing import Any
from ..classes import Team, Driver


RCPATH = os.path.abspath(os.path.join("src", "data", "racing-categories"))


def path_to_category(category: str):
    return os.path.abspath(os.path.join("src", "data", "racing-categories", category))

def path_to_class(category: str, racing_class: str):
    return os.path.abspath(os.path.join(path_to_category(category), racing_class))


def get_racing_categories_list():
    return [category_name for category_name in os.listdir(RCPATH) if os.path.isdir(os.path.join(RCPATH, category_name))]

def get_classes_from_category(category: str):
    path = path_to_category(category)
    return [class_name for class_name in os.listdir(path) if os.path.isdir(os.path.join(path, class_name))]


def get_racing_categories_dict():
    result: dict = {}
    for category_name in os.listdir(RCPATH):
        result.update({category_name: [class_name for class_name in os.listdir(path_to_category(category_name))]})

    return result


RACING_CATEGORY = "Volo"
RACING_CLASS = "CAT-B"

PATH_TEAMS   = os.path.abspath(os.path.join(path_to_class(RACING_CATEGORY, RACING_CLASS), "teams"))
PATH_DRIVERS = os.path.abspath(os.path.join(path_to_class(RACING_CATEGORY, RACING_CLASS), "drivers"))
PATH_TRACKS  = os.path.abspath(os.path.join(path_to_class(RACING_CATEGORY, RACING_CLASS), "tracks"))



# MANIFEST / SETUP

def read_manifest(path_to_class):
    with open(os.path.join(path_to_class, ".manifest"), "r") as file:
        return json.load(file)


from .link import physics
physics.init(read_manifest(path_to_class(RACING_CATEGORY, RACING_CLASS))['slipstream-effectiveness'])


# TEAM / DRIVER

def team_write(info: str, value: Any) -> None:
    with open(PATH_TEAMS, "r") as file:
        data = json.load(file)

    data[info] = value

    with open(PATH_TEAMS, "w") as file:
        json.dump(data, file, indent=4)


def team_show() -> dict:
    with open(PATH_TEAMS, "r") as file:
        return json.load(file)


def driver_write(info: str, value: Any) -> None:
    with open(PATH_DRIVERS, "r") as file:
        data = json.load(file)

    data[info] = value

    with open(PATH_DRIVERS, "w") as file:
        json.dump(data, file, indent=4)


def driver_show() -> dict:
    with open(PATH_DRIVERS, "r") as file:
        return json.load(file)


def ready_drivers() -> list[Driver]:
    DRIVERS: list[Driver] = []
    TEAMS: dict[int, Team] = {}

    for team_name in (teams := team_show()):
        TEAMS.update({
            teams[team_name]['id']: Team(team_name, teams[team_name])
        })

    for team_name in (teams := team_show()):
        for driver_name in (drivers := driver_show()):
            for n in teams[team_name]['drivers']:
                if n == drivers[driver_name]['number']:
                    DRIVERS.append(Driver(driver_name, TEAMS[drivers[driver_name]['team-id']], drivers[driver_name]['number'], drivers[driver_name]['skills']))

    return DRIVERS



# TRACK

def track_show() -> Any:
    with open(PATH_TRACKS, "r") as file:
        return json.load(file)


def convert_track_to_points(track: list[list]):
    TRACK_POINTS = [(x, y) for x, y, *_ in track]
    return TRACK_POINTS

def scale_track_points(track_points: list[tuple[int, int]]) -> list:
    SCALED_POINTS = [(x / 2, y / 2) for x, y in track_points]
    return SCALED_POINTS