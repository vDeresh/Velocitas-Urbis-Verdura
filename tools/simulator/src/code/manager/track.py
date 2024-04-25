import json
from os import path
from typing import Any

PATH = path.abspath(path.join("src", "data", "tracks"))


def write(info: str, value: Any) -> None:
    with open(PATH, "r") as file:
        data = json.load(file)

    data[info] = value

    with open(PATH, "w") as file:
        json.dump(data, file, indent=4)


def show() -> Any:
    with open(PATH, "r") as file:
        return json.load(file)



def convert_track_to_points(track: list[list]):
    TRACK_POINTS = [(x, y) for x, y, *_ in track]
    return TRACK_POINTS

def scale_track_points(track_points: list[tuple[int, int]]) -> list:
    SCALED_POINTS = [(x / 2, y / 2) for x, y in track_points]
    return SCALED_POINTS