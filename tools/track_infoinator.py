import sys
import json
from os import path
from pygame.math import Vector2


def show():
    with open(path.abspath(path.join("src", "data", "racing-categories", sys.argv[1], "tracks")), "r") as file:
        return json.load(file)


TRACK = show()[sys.argv[2]]['track']

TRACK_POINTS = []
for x, y, *_ in show()[sys.argv[2]]['track']:
    TRACK_POINTS.append((x, y))


print("Track:")
print(TRACK)

length = 0
for n in range(len(TRACK_POINTS) - 1):
    length += Vector2(TRACK_POINTS[n]).distance_to(TRACK_POINTS[n + 1])


starting_direction = Vector2(TRACK_POINTS[0][0] - TRACK_POINTS[-1][0], TRACK_POINTS[0][1] - TRACK_POINTS[-1][1]).normalize()


avg_rts = 0
avg_divider_counter = 0

for p in TRACK:
    if "turn-start" in p[2]:
        avg_rts += p[2][-1]["reference-target-speed"]
        avg_divider_counter += 1

avg_rts /= avg_divider_counter


pitlane_entry_point = -1

for n, p in enumerate(TRACK):
    if "pit-lane-entry" in p[2]:
        pitlane_entry_point = n


pitlane_exit_point = -1

for n, p in enumerate(TRACK):
    if "pit-lane-exit" in p[2]:
        pitlane_exit_point = n


print()
print("Track length (km / m / sd) >", length / 1000, "/", length, "/", length / 2)
print("Starting direction >", starting_direction)
print("Average reference target speed >", avg_rts)
print("Point count >", len(TRACK_POINTS))
print("Pit lane entry point >", pitlane_entry_point)
print("Pit lane exit point >", pitlane_exit_point)