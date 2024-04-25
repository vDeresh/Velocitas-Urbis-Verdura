from pygame.math import Vector2
from .others import distance_between_points, next_turn_data, is_it_end_of_turn, distance_to_pit_lane_entry #, is_it_pit_entry
from ..code.manager import link
import random


class Team:
    def __init__(self, name: str, data: dict) -> None:
        self.name = name
        self.id = data['id']
        self.drivers = data['drivers']
        self.color = data['color']
        self.name_abbreviation = data['name-abbreviation']
        self.car_stats = data['car-stats']


class Driver:
    def __init__(self, name: str, team: Team, number: int, skills: dict[str, float]) -> None:
        self.name = name
        self.team = team
        self.number = number
        self.skills: dict[str, float] = skills

        self.pos: Vector2 = Vector2(0, 0)
        self.speed: float = 0
        self.tyre_wear: float = 1
        self.tyre_type: int

        self.current_point: int = 0
        self.next_point_xy: list[int] = [2048, 2048]
        self.lap: int = 1
        self.position: int
        self.prev_position: int
        self.was_overtaken: float = 120 * self.skills['reaction-time-multiplier']
        self.is_already_turning: int = 0

        self.decision_stack: list[dict] = [] # [{"type": "pit"}]

        self.pit_path_points: list
        self.on_pitlane: bool = False
        self.pitting: bool = False
        self.pitlane_speed_limit_on: bool = False
        self.pitstop_timer: float

    def init(self, track, position: int, tyre_type: int, racing_allowed: bool) -> None:
        self.next_turn_data = next_turn_data(track, self.current_point)
        self.position = self.prev_position = position
        self.tyre_type = tyre_type

        self.racing_allowed = racing_allowed

    def calculate_speed(self, track_points: list, drivers: list) -> float:
        if self.distance_to_next_turn and self.next_turn_data:
            return link.calculate_speed(self.is_already_turning, self.speed, self.distance_to_next_turn, self.tyre_wear, self.tyre_type, self.skills['breaking'], self.next_turn_data[2][-1]['reference-target-speed'], self.team.car_stats['mass'], self.team.car_stats['downforce'], self.team.car_stats['drag'], self.distance_to_next_driver_squared, drivers[self.position - 1 - 1].speed, drivers[self.position - 1 - 1].team.car_stats['downforce'], self.was_overtaken)
        return self.speed

    def slipstream_multiplier(self, drivers: list) -> float:
        return link.calculate_slipstream_multiplier(self.distance_to_next_driver_squared, drivers[self.position - 1 - 1].speed, drivers[self.position - 1 - 1].team.car_stats['downforce'], self.was_overtaken)

    def set_pos(self, x: float, y: float) -> None:
        self.pos = Vector2(x, y)

    def update(self, track: list[list], track_points: list, pitlane: list, pitlane_points: list, track_info: dict, drivers: list) -> None:
        self.distance_to_next_turn = self.pos.distance_to((self.next_turn_data[0], self.next_turn_data[1]))
        # self.distance_to_next_driver = distance_to_next_driver(track_info['length'], track_points, self, drivers)
        self.distance_to_next_driver_squared = distance_to_next_driver(track_info['length'], track_points, self, drivers)

        # Calls
        for call in self.decision_stack:
            match call['type']:
                case "pit":
                    if (not self.is_already_turning) and (self.current_point + 60 > track_info['pit-lane-entry-point']) and (not self.on_pitlane) and (self.distance_to_next_turn > distance_to_pit_lane_entry(track_info['length'], track, self.current_point, self.pos.distance_to(self.next_point_xy[:2]), track_info['pit-lane-entry-point'])):
                        self.pit_to_tyre_type = call['tyre']
                        self.on_pitlane = True
                        # self.pit_path_points = track_points[self.current_point : track_info['pit-lane-entry-point'] - 1]
                        # self.pit_path_points = pitlane_points
                        self.current_point = 0
                        self.pitstop_timer = 0
                        self.decision_stack.remove(call)
                        break

        # Pitting
        if self.on_pitlane:
            if self.pitlane_speed_limit_on:
                self.speed = track_info['pit-lane-speed-limit']

            if self.pos == self.next_point_xy:
                self.current_point += 1

            if self.current_point + 1 < len(pitlane_points):
                self.next_point_xy = pitlane_points[self.current_point + 1][0 : 2]

                if "speed-limit-start" in pitlane[self.current_point][2]:
                    self.pitlane_speed_limit_on = True

                elif "speed-limit-end" in pitlane[self.current_point][2]:
                    self.pitlane_speed_limit_on = False


            if "pit-box" in pitlane[self.current_point][2] and self.team.id == pitlane[self.current_point][2][1]:
                self.speed = 0
                self.pitstop_timer += 1 / 60 # 1 / FPS
                if self.pitstop_timer >= 2 * self.skills['reaction-time-multiplier']:
                    self.current_point += 1
                    self.tyre_wear = 1
                    self.tyre_type = self.pit_to_tyre_type
                    del self.pit_to_tyre_type

            if "pit-lane-exit" in pitlane[self.current_point][2]:
                self.on_pitlane = False
                self.pitting = False
                self.pitlane_speed_limit_on = False

                self.current_point = track_info['pit-lane-exit-point']
                self.next_point_xy = track_points[self.current_point + 1]

            self.pos = self.pos.move_towards(self.next_point_xy, self.speed)
            return

        # Racing
        self.speed = self.calculate_speed(track_points, drivers)

        if self.racing_allowed:
            if self.position > self.prev_position:
                self.was_overtaken = 60 * self.skills['reaction-time-multiplier']

            if self.was_overtaken:
                self.was_overtaken -= 1
                if self.was_overtaken < 0:
                    self.was_overtaken = 0

            self.racing_logic(drivers)


        if self.distance_to_next_turn == 0:
            self.is_already_turning = 1
            # self.next_turn_data = None
        else:
            if is_it_end_of_turn(track, self.current_point):
                self.is_already_turning = 0
                self.next_turn_data = next_turn_data(track, self.current_point)


        if self.is_already_turning:
            self.tyre_wear = link.calculate_tyre_wear(self.tyre_wear, self.tyre_type, self.speed, self.next_turn_data[2][-1]['reference-target-speed'])


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
        self.prev_position = self.position

    # def post_update(self) -> None:
    #     self.prev_position = self.position

    def racing_logic(self, drivers: list) -> None: # TODO
        if self.was_overtaken: return

        slipstream = self.slipstream_multiplier(drivers)
        next_driver = drivers[self.position - 1 - 1]
        speed_of_the_next_driver = next_driver.speed

        if self.distance_to_next_driver_squared < 256:
            if self.number == 1:
                pass

            if next_driver.distance_to_next_driver_squared < 64:
                self.speed = min(self.speed * slipstream, speed_of_the_next_driver)
                # print("Opponent is already fighting")

            elif (self.distance_to_next_turn < 200) and (self.skills['attack'] - next_driver.skills['defence'] * self.next_turn_data[2][-1]['overtaking-risk'] < random.random()):
                self.speed *= slipstream
                # print("Overtake 1")

            elif self.distance_to_next_turn < 400:
                self.speed = min(self.speed * slipstream, speed_of_the_next_driver)
                # print("Waiting for the corner")

            else:
                self.speed *= slipstream
                # print("else 2")

        else:
            self.speed *= slipstream
            # print("else 1")


def distance_to_next_driver(track_length: float, track_points: list, driver1: Driver, drivers: list[Driver]) -> float:
    next_driver = drivers[driver1.position - 1 - 1]

    if (driver1.position != 1) and (driver1.current_point == next_driver.current_point):
        return driver1.pos.distance_to(next_driver.pos)
    else:
        temp1 = driver1.pos.distance_to(driver1.next_point_xy)
        temp2 = distance_between_points(track_length, track_points, driver1.current_point + 1, next_driver.current_point)
        temp3 = next_driver.pos.distance_to(track_points[next_driver.current_point])

        return temp1 + temp2 + temp3


def distance_to_next_driver_squared(track_length: float, track_points: list, driver1: Driver, drivers: list[Driver]) -> float:
    next_driver = drivers[driver1.position - 1 - 1]

    if (driver1.position != 1) and (driver1.current_point == next_driver.current_point):
        return driver1.pos.distance_to(next_driver.pos)
    else:
        temp1 = driver1.pos.distance_to(driver1.next_point_xy)
        temp2 = distance_between_points(track_length, track_points, driver1.current_point + 1, next_driver.current_point)
        temp3 = next_driver.pos.distance_to(track_points[next_driver.current_point])

        return temp1 + temp2 + temp3