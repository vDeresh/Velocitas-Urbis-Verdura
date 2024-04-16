import sys
import json
from os import path
from pygame.math import Vector2
from math import sqrt


def show():
    with open(path.abspath(path.join("src", "data", "tracks")), "r") as file:
        return json.load(file)


TRACK = show()[sys.argv[1]]['track']
NEW_TRACK = []

for n, p in enumerate(TRACK):
    NEW_TRACK.append([p[0] * 2, p[1] * 2, p[2:][0]])

print(NEW_TRACK)


with open(path.abspath(path.join("src", "data", "tracks")), "r") as file:
    data = json.load(file)

data[sys.argv[1]]['track'] = NEW_TRACK

with open("track_conventer_output.json", "w") as file:
    json.dump(data, file, indent=None, separators=(", ", ": "))