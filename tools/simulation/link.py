import ctypes
from os import path

physics = ctypes.CDLL(path.abspath(path.join("tools", "simulation", "physics.dll")))


# class Vector(ctypes.Structure):
#     _fields_ = [('x', ctypes.c_float), ('y', ctypes.c_float)]


physics.init.argtypes = []
physics.init.restype = None
physics.init()

# double handle(int alreadyTurning, double currentSpeed, double distanceToTurn, double tyreWear, double driversBrakingSkill,
#              double referenceTargetSpeed, double mass, double downforce, double drag,
#              double distanceToCarAhead, double speedOfCarAhead, double downforceOfCarAhead)
physics.handle.argtypes = [ctypes.c_int, ctypes.c_double, ctypes.c_double, ctypes.c_double, ctypes.c_double, ctypes.c_double, ctypes.c_double, ctypes.c_double, ctypes.c_double, ctypes.c_double, ctypes.c_double, ctypes.c_double, ctypes.c_float]
physics.handle.restype = ctypes.c_double


def calculate_speed(alreadyTurning: int, currentSpeed: float, distanceToTurn: float, tyreWear: float, driversBrakingSkill: float, referenceTargetSpeed: float, mass: float, downforce: float, drag: float, distanceToCarAhead: float, speedOfCarAhead: float, downforceOfCarAhead: float, wasOvertaken: float) -> float:
    return physics.handle(ctypes.c_int(alreadyTurning), ctypes.c_double(currentSpeed), ctypes.c_double(distanceToTurn), ctypes.c_double(tyreWear), ctypes.c_double(driversBrakingSkill), ctypes.c_double(referenceTargetSpeed), ctypes.c_double(mass), ctypes.c_double(downforce), ctypes.c_double(drag), ctypes.c_double(distanceToCarAhead), ctypes.c_double(speedOfCarAhead), ctypes.c_double(downforceOfCarAhead), ctypes.c_float(wasOvertaken))