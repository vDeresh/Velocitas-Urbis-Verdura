import sys
import json
from os import path


def show():
    with open(path.abspath(path.join("src", "data", "racing-categories", sys.argv[1], "tracks")), "r") as file:
        return json.load(file)


TRACK: list[list[list]] = show()[sys.argv[2]]['track']

print("Track:")
print(TRACK)


for n, p in enumerate(TRACK):
    if "timer" in p[2]:
        TRACK[n][2].remove("timer")


for n, p in enumerate(TRACK):
    if not n % 10:
        TRACK[n][2].insert(0, "timer")

print("Modified track:")
print(TRACK)


with open("test.json", "w") as file:
    json.dump(TRACK, file, indent=None)

with open("test.json", "r+") as file:
    content = file.read()
    content = content.replace("]], ", "]],\n").replace("\n", "\n    ")
    content = content.replace("[[", "[\n    [", 1)
    file.seek(0)
    file.write(content)
    file.truncate()


with open("test.json", "r") as file:
    for n, p in enumerate(json.load(file)):
        if "timer" in p[2]:
            print(n, end=", ")