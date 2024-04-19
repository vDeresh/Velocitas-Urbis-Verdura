import ctypes
from os import path

physics      = ctypes.CDLL(path.abspath(path.join("src", "shared", "physics.dll")))
# calculations = ctypes.CDLL(path.abspath(path.join("src", "shared", "calculations.dll")))
# """
# `float distanceBetweenPoints(float (*track)[2], int p1, int p2)`
# """


# double handleSpeed(int alreadyTurning, double currentSpeed, double distanceToTurn, double tyreWear, double driversBrakingSkill,
#              double referenceTargetSpeed, double mass, double downforce, double drag,
#              double distanceToCarAhead, double speedOfCarAhead, double downforceOfCarAhead)
physics.handleSpeed.argtypes = [ctypes.c_int, ctypes.c_double, ctypes.c_double, ctypes.c_double, ctypes.c_double, ctypes.c_double, ctypes.c_double, ctypes.c_double, ctypes.c_double, ctypes.c_double, ctypes.c_double, ctypes.c_double, ctypes.c_double, ctypes.c_float]
physics.handleSpeed.restype = ctypes.c_double

def calculate_speed(alreadyTurning: int, currentSpeed: float, distanceToTurn: float, tyreWear: float, tyreType: float, driversBrakingSkill: float, referenceTargetSpeed: float, mass: float, downforce: float, drag: float, distanceToCarAhead: float, speedOfCarAhead: float, downforceOfCarAhead: float, wasOvertaken: float) -> float:
    return physics.handleSpeed(ctypes.c_int(alreadyTurning), ctypes.c_double(currentSpeed), ctypes.c_double(distanceToTurn), ctypes.c_double(tyreWear), ctypes.c_double(tyreType), ctypes.c_double(driversBrakingSkill), ctypes.c_double(referenceTargetSpeed), ctypes.c_double(mass), ctypes.c_double(downforce), ctypes.c_double(drag), ctypes.c_double(distanceToCarAhead), ctypes.c_double(speedOfCarAhead), ctypes.c_double(downforceOfCarAhead), ctypes.c_float(wasOvertaken))


# double handleTyreWear(double tyreWear, int tyreType, double speed, double targetSpeed)
physics.handleTyreWear.argtypes = [ctypes.c_double, ctypes.c_int, ctypes.c_double, ctypes.c_double]
physics.handleTyreWear.restype = ctypes.c_double

def calculate_tyre_wear(tyreWear: float, tyreType: int, speed: float, targetSpeed: float) -> float:
    return physics.handleTyreWear(ctypes.c_double(tyreWear), ctypes.c_int(tyreType), ctypes.c_double(speed), ctypes.c_double(targetSpeed))


# calculations.process_coordinates.argtypes = (ctypes.POINTER(ctypes.c_float * 2), ctypes.c_int)
# calculations.process_coordinates.restype = None

# calculations.distanceBetweenPoints.argtypes = (ctypes.POINTER(ctypes.c_float * 2), ctypes.c_int, ctypes.c_int)
# calculations.distanceBetweenPoints.restype = ctypes.c_float