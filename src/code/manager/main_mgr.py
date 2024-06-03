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


def get_racing_categories_dict() -> dict[str, list[str]]:
    result: dict = {}
    for category_name in os.listdir(RCPATH):
        result.update({category_name: [class_name for class_name in os.listdir(path_to_category(category_name))]})

    return result


# RACING_CATEGORY = "Volo"
# RACING_CLASS = "CAT-B"
# RACE_TRACK = "sc1"

# PATH_TEAMS   = os.path.abspath(os.path.join(path_to_class(RACING_CATEGORY, RACING_CLASS), "teams"))
# PATH_DRIVERS = os.path.abspath(os.path.join(path_to_class(RACING_CATEGORY, RACING_CLASS), "drivers"))
# PATH_TRACK   = os.path.abspath(os.path.join("src", "data", "tracks", RACE_TRACK))



# MANIFEST / SETUP

def read_manifest(racing_category: str, racing_class: str):
    with open(os.path.join(path_to_class(racing_category, racing_class), ".manifest"), "r") as file:
        return json.load(file)

def init(racing_category: str, racing_class: str) -> None:
    from .link import physics
    physics.init(read_manifest(racing_category, racing_class)['slipstream-effectiveness'])

def get_features(racing_category_name: str, racing_class_name: str, race_track_name: str) -> dict[str, bool] | None:
    manifest = read_manifest(racing_category_name, racing_class_name)
    track = track_show(race_track_name)

    if manifest['racing-type'] in track['allowed-racing-types']:
        return track[manifest['racing-type']]['features']
    else:
        return



# TEAM / DRIVER

# def team_write(info: str, value: Any) -> None:
#     with open(PATH_TEAMS, "r") as file:
#         data = json.load(file)

#     data[info] = value

#     with open(PATH_TEAMS, "w") as file:
#         json.dump(data, file, indent=4)


def teams_show(racing_category_name: str, racing_class_name: str) -> dict:
    with open(os.path.abspath(os.path.join(path_to_class(racing_category_name, racing_class_name), "teams")), "r") as file:
        return json.load(file)


# def driver_write(info: str, value: Any) -> None:
#     with open(PATH_DRIVERS, "r") as file:
#         data = json.load(file)

#     data[info] = value

#     with open(PATH_DRIVERS, "w") as file:
#         json.dump(data, file, indent=4)


def drivers_show(racing_category_name: str, racing_class_name: str) -> dict:
    with open(os.path.abspath(os.path.join(path_to_class(racing_category_name, racing_class_name), "drivers")), "r") as file:
        return json.load(file)


def ready_drivers(racing_category_name: str, racing_class_name: str) -> list[Driver]:
    DRIVERS: list[Driver] = []
    TEAMS: dict[int, Team] = {}

    for team_name in (teams := teams_show(racing_category_name, racing_class_name)):
        TEAMS.update({
            teams[team_name]['id']: Team(team_name, teams[team_name])
        })

    for team_name in (teams := teams_show(racing_category_name, racing_class_name)):
        for driver_name in (drivers := drivers_show(racing_category_name, racing_class_name)):
            for n in teams[team_name]['drivers']:
                if n == drivers[driver_name]['number']:
                    DRIVERS.append(Driver(driver_name, TEAMS[drivers[driver_name]['team-id']], drivers[driver_name]['number'], drivers[driver_name]['skills']))

    return DRIVERS



# TRACK

def show_all_tracks() -> list[str]:
    return os.listdir(os.path.abspath(os.path.join("src", "data", "tracks")))

def track_show(race_track_name: str) -> Any:
    with open(os.path.abspath(os.path.join("src", "data", "tracks", race_track_name)), "r") as file:
        return json.load(file)

def convert_track_to_points(track: list[list]):
    TRACK_POINTS = [(x, y) for x, y, *_ in track]
    return TRACK_POINTS

def scale_track_points(track_points: list[tuple[int, int]], track_scale: float) -> list:
    SCALED_POINTS = [(x / 2 / track_scale, y / 2 / track_scale) for x, y in track_points]
    return SCALED_POINTS



# if read_manifest(RACING_CATEGORY, RACING_CLASS)['racing-type'] not in track_show()['allowed-racing-types']:
#     raise ValueError(f"{RACING_CATEGORY}\\{RACING_CLASS} is not allowed on track {RACE_TRACK}")