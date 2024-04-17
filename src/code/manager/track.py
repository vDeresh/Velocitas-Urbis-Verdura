import json
from os import path

def show():
    with open(path.abspath(path.join("tools", "simulation", "data", "tracks")), "r") as file:
        return json.load(file)

def convert_track_to_points(track: list[list]):
    TRACK_POINTS = [(x, y) for x, y, *_ in track]
    return TRACK_POINTS

def scale_track_points(track_points):
    return [(x / 2, y / 2) for x, y in track_points]