import ctypes
from os import path

physics      = ctypes.CDLL(path.abspath(path.join("src", "shared", "physics.dll")))
# calculations = ctypes.CDLL(path.abspath(path.join("src", "shared", "calculations.dll")))
# """
# `float distanceBetweenPoints(float (*track)[2], int p1, int p2)`
# """


physics.init.argtypes = [ctypes.c_float]
physics.init.restype = None
# physics.init() # init in main_mgr.py


# double handleSpeed(int alreadyTurning, double currentSpeed, double distanceToTurn, double tyreWear, double tyreType, double driversBrakingSkill,
#                    double referenceTargetSpeed, double mass, double downforce, double drag,
#                    double distanceToCarAhead, double speedOfCarAhead, double downforceOfCarAhead, float wasOvertaken,
#                    double ultimateAccelerationMultiplier3000,
#                    double maxSpeed,
#                    int gear)
physics.handleSpeed.argtypes = [ctypes.c_int, ctypes.c_double, ctypes.c_double, ctypes.c_double, ctypes.c_double, ctypes.c_double, ctypes.c_double, ctypes.c_double, ctypes.c_double, ctypes.c_double, ctypes.c_double, ctypes.c_double, ctypes.c_double, ctypes.c_float, ctypes.c_double, ctypes.c_double, ctypes.c_int]
physics.handleSpeed.restype = ctypes.c_double

def calculate_speed(alreadyTurning: int, currentSpeed: float, distanceToTurn: float, tyreWear: float, tyreType: float, driversBrakingSkill: float, referenceTargetSpeed: float, mass: float, downforce: float, drag: float, distanceToCarAhead: float, speedOfCarAhead: float, downforceOfCarAhead: float, wasOvertaken: float, ultimateAccelerationMultiplier3000: float, maxSpeed: float, gear: int) -> float:
    return physics.handleSpeed(alreadyTurning, currentSpeed, distanceToTurn, tyreWear, tyreType, driversBrakingSkill, referenceTargetSpeed, mass, downforce, drag, distanceToCarAhead, speedOfCarAhead, downforceOfCarAhead, wasOvertaken, ultimateAccelerationMultiplier3000, maxSpeed, gear)


# double slipstreamMultiplier(double distanceToCarAhead, double speedOfCarAhead, double downforceOfCarAhead, double speed, float wasOvertaken)
# physics.slipstreamMultiplier.argtypes = [ctypes.c_double, ctypes.c_double, ctypes.c_double, ctypes.c_float]
# physics.slipstreamMultiplier.restype = ctypes.c_double

# def calculate_slipstream_multiplier(distanceToCarAhead: float, speedOfCarAhead: float, downforceOfCarAhead: float, wasOvertaken: float) -> float:
#     return physics.slipstreamMultiplier(ctypes.c_double(distanceToCarAhead), ctypes.c_double(speedOfCarAhead), ctypes.c_double(downforceOfCarAhead), ctypes.c_float(wasOvertaken))


# double handleTyreWear(double tyreWear, int tyreType, double speed, double targetSpeed)
physics.handleTyreWear.argtypes = [ctypes.c_double, ctypes.c_int, ctypes.c_double, ctypes.c_double]
physics.handleTyreWear.restype = ctypes.c_double

def calculate_tyre_wear(tyreWear: float, tyreType: int, speed: float, targetSpeed: float) -> float:
    return physics.handleTyreWear(tyreWear, tyreType, speed, targetSpeed)


# double maxSpeed(double drag, double mass, double downforce)
physics.maxSpeed.argtypes = [ctypes.c_double, ctypes.c_double, ctypes.c_double]
physics.maxSpeed.restype = ctypes.c_double

def max_speed(drag: float, mass: float, downforce: float) -> float:
    return physics.maxSpeed(ctypes.c_double(drag), ctypes.c_double(mass), ctypes.c_double(downforce))


# double handleQualiSpeed(int alreadyTurning, double currentSpeed, double distanceToTurn, double tyreWear, int tyreType, double driversBrakingSkill,
#                         double referenceTargetSpeed, double mass, double downforce, double drag,
#                         double ultimateAccelerationMultiplier3000,
#                         double maxSpeed,
#                         int gear)
physics.handleQualiSpeed.argtypes = [ctypes.c_int, ctypes.c_double, ctypes.c_double, ctypes.c_double, ctypes.c_int, ctypes.c_double, ctypes.c_double, ctypes.c_double, ctypes.c_double, ctypes.c_double, ctypes.c_double, ctypes.c_double, ctypes.c_int]
physics.handleQualiSpeed.restype = ctypes.c_double

def calculate_quali_speed(alreadyTurning: int, currentSpeed: float, distanceToTurn: float, tyreWear: float, tyreType: int, driversBrakingSkill: float, referenceTargetSpeed: float, mass: float, downforce: float, drag: float, ultimateAccelerationMultiplier3000: float, maxSpeed: float, gear: int):
    return physics.handleQualiSpeed(alreadyTurning, currentSpeed, distanceToTurn, tyreWear, tyreType, driversBrakingSkill, referenceTargetSpeed, mass, downforce, drag, ultimateAccelerationMultiplier3000, maxSpeed, gear)

# calculations.process_coordinates.argtypes = (ctypes.POINTER(ctypes.c_float * 2), ctypes.c_int)
# calculations.process_coordinates.restype = None

# calculations.distanceBetweenPoints.argtypes = (ctypes.POINTER(ctypes.c_float * 2), ctypes.c_int, ctypes.c_int)
# calculations.distanceBetweenPoints.restype = ctypes.c_float