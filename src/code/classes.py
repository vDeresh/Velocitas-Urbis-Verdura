from pygame.math import Vector2
from .others import distance_between_points, next_turn_data, is_it_end_of_turn, distance_to_pit_lane_entry #, is_it_pit_entry
from ..code.manager import link

import random
# from time import perf_counter


def distance_to_next_driver(track_length: float, track_points: list, driver1, drivers: list) -> float:
    next_driver = drivers[driver1.position - 1 - 1]

    if (driver1.position != 1) and (driver1.current_point == next_driver.current_point):
        return driver1.pos.distance_to(next_driver.pos)
    else:
        temp1 = driver1.pos.distance_to(driver1.next_point_xy)
        temp2 = distance_between_points(track_length, track_points, driver1.current_point + 1, next_driver.current_point)
        temp3 = next_driver.pos.distance_to(track_points[next_driver.current_point])

        return temp1 + temp2 + temp3


class Team:
    def __init__(self, name: str, data: dict) -> None:
        self.name: str = name
        self.id: int = data['id']
        self.drivers: list = data['drivers']
        self.color: str = data['color']
        self.name_abbreviation: str = data['name-abbreviation']
        self.car_stats: dict = data['car-stats']


class Driver:
    def __init__(self, full_name: str, team: Team, number: int, skills: dict[str, float]) -> None:
        self.full_name = full_name
        self.name = full_name.split(" ")
        self.team = team
        self.number = number
        self.skills: dict[str, float] = skills

        self.pos: Vector2 = Vector2(0, 0)
        self.speed: float = 0
        self.max_speed: float = link.max_speed(team.car_stats['drag'], team.car_stats['mass'], team.car_stats['downforce'])
        self.tyre_wear: float = 1
        self.tyre_type: int

        self.current_point: int = 0
        self.next_point_xy: list[int] # = [2048, 2048]
        self.lap: int = 1
        self.position: int
        self.prev_position: int
        self.was_overtaken: float = 0
        self.is_already_turning: int = 0

        self.call_stack: list[dict] = [] # [{"type": "pit"}]

        self.pit_path_points: list
        self.on_pitlane: bool = False
        # self.pitting: bool = False
        self.pitlane_speed_limit_on: bool = False
        self.pit_exit: bool = False
        self.pitstop_timer: float

        # self.overtaking: float = 0
        self.drs_zone: bool = False
        self.drs_available: float
        self.drs_active: bool = False

        self.time_difference: float = 0

        self.slow: bool = False

        # QUALIFICATIONS
        # self.time: float = 0 # in seconds
        self.coming_back: bool = False
        # self.flying_lap: bool
        self.quali_lap_time_timer: float = -1
        self.quali_best_lap_time: float = float("inf")

    @property
    def downforce(self) -> float:
        if self.drs_active:
            return min(0.1, self.team.car_stats['downforce'] - (self.team.car_stats['downforce'] * self.team.car_stats['drs-efficiency']))
        return self.team.car_stats['downforce']

    @property
    def gear(self) -> int:
        if self.speed > self.max_speed / 1.1:
            return 8
        if self.speed > self.max_speed / 1.3:
            return 7
        if self.speed > self.max_speed / 1.45:
            return 6
        if self.speed > self.max_speed / 1.7:
            return 5
        if self.speed > self.max_speed / 2.2:
            return 4
        if self.speed > self.max_speed / 2.6:
            return 3
        if self.speed > self.max_speed / 3:
            return 2
        return 1

    def init(self, track, position: int, tyre_type: int) -> None:
        self.next_turn_data = next_turn_data(track, self.current_point)
        self.position = self.prev_position = position
        self.tyre_type = tyre_type
        self.next_point_xy = track[self.current_point][0 : 2]

    def calculate_speed(self, distance_to_braking_finish_point: float, reference_target_speed: float, drivers: list, ultimateAccelerationMultiplier3000: float) -> float: # track_points: list
        if distance_to_braking_finish_point:
            if self.slow:
                _temp_speed = link.calculate_speed(self.is_already_turning, self.speed * 1.5, distance_to_braking_finish_point, self.tyre_wear, self.tyre_type, self.skills['braking'], reference_target_speed, self.team.car_stats['mass'], self.downforce, self.team.car_stats['drag'], self.distance_to_next_driver, drivers[self.position - 1 - 1].speed, drivers[self.position - 1 - 1].team.car_stats['downforce'], self.was_overtaken, ultimateAccelerationMultiplier3000, self.max_speed, self.gear) / 1.5

                if self.distance_to_next_driver < 6:
                    min(_temp_speed, drivers[self.position - 1 - 1].speed)
                else:
                    return _temp_speed
            else:
                return link.calculate_speed(self.is_already_turning, self.speed, distance_to_braking_finish_point, self.tyre_wear, self.tyre_type, self.skills['braking'], reference_target_speed, self.team.car_stats['mass'], self.downforce, self.team.car_stats['drag'], self.distance_to_next_driver, drivers[self.position - 1 - 1].speed, drivers[self.position - 1 - 1].team.car_stats['downforce'], self.was_overtaken, ultimateAccelerationMultiplier3000, self.max_speed, self.gear)
        return self.speed

    def calculate_quali_speed(self, ultimateAccelerationMultiplier3000: float) -> float:
        if self.distance_to_next_turn:
            return link.calculate_quali_speed(self.is_already_turning, self.speed, self.distance_to_next_turn, self.tyre_wear, self.tyre_type, self.skills['braking'], self.next_turn_data[2][-1]['reference-target-speed'], self.team.car_stats['mass'], self.downforce, self.team.car_stats['drag'], ultimateAccelerationMultiplier3000, self.max_speed, self.gear)
        return self.speed

    # def slipstream_multiplier(self, drivers: list) -> float:
    #     return link.calculate_slipstream_multiplier(self.distance_to_next_driver, drivers[self.position - 1 - 1].speed, drivers[self.position - 1 - 1].team.car_stats['downforce'], self.was_overtaken)

    def set_pos(self, x: float, y: float) -> None:
        self.pos = Vector2(x, y)

    def update(self, track: list[list], track_points: list, pitlane: list, pitlane_points: list, track_info: dict, drivers: list) -> None:
        self.distance_to_next_turn = self.pos.distance_to((self.next_turn_data[0], self.next_turn_data[1]))
        self.distance_to_next_driver = distance_to_next_driver(track_info['length'], track_points, self, drivers)

        # Calls -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        for call in self.call_stack:
            match call['type']:
                case "pit":
                    if (not self.is_already_turning) and (self.current_point + 60 > track_info['pit-lane-entry-point']) and (not self.on_pitlane) and (self.distance_to_next_turn > distance_to_pit_lane_entry(track_info['length'], track, self.current_point, self.pos.distance_to(self.next_point_xy[:2]), track_info['pit-lane-entry-point'])):
                        self.pit_to_tyre_type = call['tyre']
                        self.on_pitlane = True
                        self.pit_exit = False
                        # self.pit_path_points = track_points[self.current_point : track_info['pit-lane-entry-point'] - 1]
                        # self.pit_path_points = pitlane_points
                        self.current_point = 0
                        self.pitstop_timer = 0
                        self.call_stack.remove(call)
                        break
        # ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- calls


        # Pitting -----------------------------------------------------------------------------------------------
        if self.on_pitlane:
            if self.pitlane_speed_limit_on:
                self.speed = track_info['pit-lane-speed-limit']
            elif self.pit_exit:
                self.speed = self.calculate_speed(self.distance_to_next_turn, self.next_turn_data[2][-1]['reference-target-speed'], [], 1)
            else:
                self.speed = self.calculate_speed(0, track_info['pit-lane-speed-limit'], [], 1)

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
                # self.pitting = False
                self.pitlane_speed_limit_on = False
                # self.current_point = track_info['pit-lane-exit-point']
                # self.pit_path_points.clear()

                self.current_point = track_info['pit-lane-exit-point']
                self.next_point_xy = track_points[self.current_point + 1]


            # if self.pitting:
            self.pos = self.pos.move_towards(self.next_point_xy, self.speed)
            #     self.next_point_xy = pitlane_points[self.current_point + 1]
            # else:
            #     self.pos = self.pos.move_towards(self.next_point_xy, self.speed)
            return
        # ----------------------------------------------------------------------------------------------- pitting


        # Racing --------------------------------------------------------------------------------------------------------------------------------------
        # if self.drs_active:
        #     self.speed = self.calculate_speed(drivers, self.team.car_stats['drs-efficiency'])
        # else:
        self.speed = self.calculate_speed(self.distance_to_next_turn, self.next_turn_data[2][-1]['reference-target-speed'], drivers, 1)

        if not self.slow:
            self.racing_logic(track, drivers)
        # -------------------------------------------------------------------------------------------------------------------------------------- racing


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


        if self.prev_position != self.position:
            self.time_difference = -1

            if self.prev_position > self.position:
                self.was_overtaken = 10 * self.skills['reaction-time-multiplier']

        self.prev_position = self.position

    # def post_update(self) -> None:
    #     self.prev_position = self.position

    def racing_logic(self, track: list[list], drivers: list) -> None: # TODO
        # DRS ----------------------------------------------------------------
        if "drs-start" in track[self.current_point][2]:
            self.drs_zone = True
            self.drs_available = 0.1 * self.skills['reaction-time-multiplier'] * (self.time_difference <= 1) * (self.position > 1)
            self.drs_active = False

        elif "drs-end" in track[self.current_point][2]:
            self.drs_zone = False
            self.drs_available = 0
            self.drs_active = False


        if self.drs_zone:
            if self.drs_available > 0:
                self.drs_available -= 0.01
                if self.drs_available < 0:
                    self.drs_available = 0

                    self.drs_active = True
        # ---------------------------------------------------------------- drs

        # if self.position > self.prev_position:
        #     self.was_overtaken = 30 * self.skills['reaction-time-multiplier']

        if self.was_overtaken > 0:
            self.was_overtaken -= 1

            if self.was_overtaken < 0:
                self.was_overtaken = 0
            else:
                return

        # slipstream = self.slipstream_multiplier(drivers)
        next_driver: Driver = drivers[self.position - 1 - 1]
        speed_of_the_next_driver = next_driver.speed

        # print()
        # print(self.number, self.distance_to_next_driver)

        # if self.overtaking:
        #     self.overtaking -= 1
        #     if self.overtaking < 0:
        #         self.overtaking = 0

        #     # self.speed *= 1.00002
            # if self.position < self.prev_position:
            #     self.overtaking = 1 * 60 * self.skills['reaction-time-multiplier']
        #     return

        if (self.distance_to_next_driver > 4) and (self.distance_to_next_driver < 500) and (next_driver.next_turn_data[2][-1]['reference-target-speed'] == self.next_turn_data[2][-1]['reference-target-speed']):
            # if next_driver.distance_to_next_driver < 4:
            #     if self.distance_to_next_driver < 6:
            #         self.speed = min(self.speed, speed_of_the_next_driver)
                # print("Opponent is already fighting")

            if (self.distance_to_next_turn < 100) and (self.skills['attack'] - self.next_turn_data[2][-1]['overtaking-risk'] + random.random() / 2 > next_driver.skills['defence']): # (self.skills['attack'] - next_driver.skills['defence'] * self.next_turn_data[2][-1]['overtaking-risk'] > random.random() * 30):
                # self.overtaking = 60 * self.skills['reaction-time-multiplier']
                pass
                # self.speed *= slipstream
                # self.speed = min(self.speed, speed_of_the_next_driver)
                # self.overtaking = 4 * 60 * self.skills['reaction-time-multiplier']
                # print("Overtake 1")

            elif self.distance_to_next_turn > 200:
                # self.overtaking = 60 * self.skills['reaction-time-multiplier']
                pass
                # self.speed = min(self.speed, speed_of_the_next_driver)
                # print("Waiting for the corner")

            else:
                if self.distance_to_next_driver < 6:
                    self.speed = min(self.speed, speed_of_the_next_driver)
                        # self.speed = self.calculate_speed(self.distance_to_next_driver, speed_of_the_next_driver, drivers, 1)
                # self.speed *= slipstream
                # self.overtaking = 4 * 60 * self.skills['reaction-time-multiplier']
                # print("Overtake 2")

        # else:
        #     self.speed *= slipstream
            # print("else 1")

    def qualifications(self, track: list[list], track_points: list, pitlane: list, pitlane_points: list, track_info: dict) -> None:
        self.distance_to_next_turn = self.pos.distance_to((self.next_turn_data[0], self.next_turn_data[1]))

        # Calls -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        for call in self.call_stack:
            match call['type']:
                case "come-back":
                    if (not self.is_already_turning) and (self.current_point + 60 > track_info['pit-lane-entry-point']) and (not self.on_pitlane) and (self.distance_to_next_turn > distance_to_pit_lane_entry(track_info['length'], track, self.current_point, self.pos.distance_to(self.next_point_xy[:2]), track_info['pit-lane-entry-point'])):
                        self.coming_back = True
                        self.on_pitlane = True
                        self.pit_exit = False
                        self.current_point = 0
                        self.pitstop_timer = 0
                        self.call_stack.remove(call)
                        break
        # ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- calls


        # Pitting -----------------------------------------------------------------------------------------------
        if self.on_pitlane:
            if self.pitlane_speed_limit_on:
                self.speed = track_info['pit-lane-speed-limit']
            elif self.pit_exit:
                self.speed = self.calculate_speed(self.distance_to_next_turn, self.next_turn_data[2][-1]['reference-target-speed'], [], 1)
            else:
                self.speed = self.calculate_speed(0, track_info['pit-lane-speed-limit'], [], 1)

            if self.pos == self.next_point_xy:
                self.current_point += 1

            if self.current_point + 1 < len(pitlane_points):
                self.next_point_xy = pitlane_points[self.current_point + 1][0 : 2]

                if "speed-limit-start" in pitlane[self.current_point][2]:
                    self.pitlane_speed_limit_on = True

                elif "speed-limit-end" in pitlane[self.current_point][2]:
                    self.pitlane_speed_limit_on = False


            if self.coming_back:
                if "pit-box" in pitlane[self.current_point][2] and self.team.id == pitlane[self.current_point][2][1]:
                    self.speed = 0
                    pass # TODO
                    # self.pitstop_timer += 1 / 60 # 1 / FPS

            if "pit-lane-exit" in pitlane[self.current_point][2]:
                self.on_pitlane = False
                # self.pitting = False
                self.pitlane_speed_limit_on = False
                # self.current_point = track_info['pit-lane-exit-point']
                # self.pit_path_points.clear()

                self.current_point = track_info['pit-lane-exit-point']
                self.next_point_xy = track_points[self.current_point + 1]


            self.pos = self.pos.move_towards(self.next_point_xy, self.speed)
            return
        # ----------------------------------------------------------------------------------------------- pitting


        # DRS ----------------------------------------------------------------
        if "drs-start" in track[self.current_point][2]:
            self.drs_zone = True
            self.drs_available = 0.1 * self.skills['reaction-time-multiplier']
            self.drs_active = False

        elif "drs-end" in track[self.current_point][2]:
            self.drs_zone = False
            self.drs_available = 0
            self.drs_active = False


        if self.drs_zone:
            if self.drs_available > 0:
                self.drs_available -= 0.01
                if self.drs_available < 0:
                    self.drs_available = 0
                    self.drs_active = True
        # ---------------------------------------------------------------- drs


        if not self.coming_back:
            self.speed = self.calculate_quali_speed(1)
        else:
            self.speed = self.calculate_quali_speed(1) / 1.5


        if self.distance_to_next_turn == 0:
            self.is_already_turning = 1
        else:
            if is_it_end_of_turn(track, self.current_point):
                self.is_already_turning = 0
                self.next_turn_data = next_turn_data(track, self.current_point)


        if self.is_already_turning:
            self.tyre_wear = link.calculate_tyre_wear(self.tyre_wear, self.tyre_type, self.speed, self.next_turn_data[2][-1]['reference-target-speed'])


        if self.pos == self.next_point_xy:
            self.current_point += 1


        self.quali_lap_time_timer += 1

        if self.current_point >= len(track):
            self.current_point = 0
            self.lap += 1

            if self.quali_lap_time_timer < self.quali_best_lap_time:
                self.quali_best_lap_time = self.quali_lap_time_timer

            self.quali_lap_time_timer = 0

            # print(f"{self.name} ({self.team.name_abbreviation}) > [{self.quali_best_lap_time}] d: {self.team.car_stats['downforce']}")


        if self.current_point + 1 < len(track):
            self.next_point_xy = track_points[self.current_point + 1]
        else:
            self.next_point_xy = track_points[0]

        self.pos = self.pos.move_towards(self.next_point_xy, self.speed)


class Timer:
    def __init__(self, track_point: int, track_point_xy: tuple[int, int]) -> None:
        self.id = track_point
        self.track_point_xy = track_point_xy
        self.cached_driver: int = 0
        self.time: float = 0