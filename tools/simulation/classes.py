from pygame.math import Vector2
from others import distance_between_points, next_turn_data, is_it_end_of_turn #, distance_to_next_driver
from link import calculate_speed


class Team:
    def __init__(self, name: str, drivers: list[int], color: str, name_abbreviation: str, car_stats: dict) -> None:
        self.name = name
        self.drivers = drivers
        self.color = color
        self.name_abbreviation = name_abbreviation
        self.car_stats = car_stats


class Driver:
    def __init__(self, team: Team, number: int, skills: dict[str, float]) -> None:
        self.team = team
        self.number = number
        self.skill_breaking = skills['breaking']
        self.reaction_time_multiplier = skills['reaction-time-multiplier']

        self.pos: Vector2 = Vector2(0, 0)
        self.speed: float = 0
        self.tyre_wear: float = 1
        # self.tyre_type: int # TODO

        self.current_point: int = 0
        self.next_point_xy: list[int] = []

        self.next_turn_data: list
        self.distance_to_next_turn: float | None = None
        self.is_already_turning: int = 0

        self.lap: int = 1
        self.position: int
        self.prev_position: int

        self.was_overtaken: float = 120 * self.reaction_time_multiplier

    def init(self, track, position: int) -> None:
        self.next_turn_data = next_turn_data(track, self.current_point)
        self.position = self.prev_position = position

    def calculate_speed(self, track_points: list, drivers: list) -> float:
        if self.distance_to_next_turn and self.next_turn_data:
            return calculate_speed(self.is_already_turning, self.speed, self.distance_to_next_turn, self.tyre_wear, self.skill_breaking, self.next_turn_data[2][-1]['reference-target-speed'], self.team.car_stats['mass'], self.team.car_stats['downforce'], self.team.car_stats['drag'], distance_to_next_driver(track_points, self, drivers), drivers[self.position - 1 - 1].speed, drivers[self.position - 1 - 1].team.car_stats['downforce'], self.was_overtaken)
        else:
            return self.speed

    def set_pos(self, x: float, y: float) -> None:
        self.pos = Vector2(x, y)

    def update(self, track: list[list], track_points: list, drivers: list) -> None:
        if self.position > self.prev_position:
            self.was_overtaken = 60 * self.reaction_time_multiplier

        if self.was_overtaken > 0:
            print("wo >", self.was_overtaken)
            self.was_overtaken -= 1

            if self.was_overtaken < 0:
                self.was_overtaken = 0


        # print(self.was_overtaken)

        self.speed = self.calculate_speed(track_points, drivers)

        self.distance_to_next_turn = self.pos.distance_to((self.next_turn_data[0], self.next_turn_data[1]))

        if self.distance_to_next_turn == 0:
            self.is_already_turning = 1
            # self.next_turn_data = None
        else:
            if is_it_end_of_turn(track, self.current_point):
                self.is_already_turning = 0
                self.next_turn_data = next_turn_data(track, self.current_point)


        if self.pos == self.next_point_xy:
            self.current_point += 1

        if self.current_point >= len(track):
            self.current_point = 0
            self.lap += 1


        if self.current_point + 1 < len(track):
            self.next_point_xy = track_points[self.current_point + 1]
        else:
            self.next_point_xy = track_points[0]

        self.pos = self.pos.move_towards(self.next_point_xy, self.speed)

    def post_update(self) -> None:
        self.prev_position = self.position

    # def racing_logic(self, track: list[list], drivers: list) -> None:
        # pass


def distance_to_next_driver(track_points: list, driver1: Driver, drivers: list[Driver]) -> float:
    next_driver = drivers[driver1.position - 1 - 1]

    if driver1.current_point == next_driver.current_point:
        d = driver1.pos.distance_to(next_driver.pos)
    else:
        temp1 = driver1.pos.distance_to(driver1.next_point_xy)
        temp2 = distance_between_points(track_points, driver1.current_point + 1, next_driver.current_point)
        temp3 = next_driver.pos.distance_to(track_points[next_driver.current_point])

        d = temp1 + temp2 + temp3

    return d * 2