from pygame.math import Vector2

def distance_between_points(track: list[list], p1: int, p2: int) -> float:
    distance = 0

    for n in range(p1, p2):
        distance += Vector2(track[n][0 : 2]).distance_to(track[n + 1][0 : 2])

    return distance

def next_turn_data(track: list[list], current_point: int) -> list:
    for p in track[current_point : len(track)]:
        if "turn-start" in p[2]:
            return p
    return track[1]

def is_it_end_of_turn(track: list[list], current_point: int) -> bool:
    if "turn-end" in track[current_point][2]:
        return True
    return False