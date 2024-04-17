import ctypes
from os import path

physics      = ctypes.CDLL(path.abspath(path.join("src", "shared", "physics.dll")))
calculations = ctypes.CDLL(path.abspath(path.join("src", "shared", "calculations.dll")))
"""
`float distanceBetweenPoints(float (*track)[2], int p1, int p2)`
"""


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



# calculations.process_coordinates.argtypes = (ctypes.POINTER(ctypes.c_float * 2), ctypes.c_int)
# calculations.process_coordinates.restype = None

calculations.distanceBetweenPoints.argtypes = (ctypes.POINTER(ctypes.c_float * 2), ctypes.c_int, ctypes.c_int)
calculations.distanceBetweenPoints.restype = ctypes.c_float

track = [[10.5, 24.7], [3.2, 7.9], [49.1, 33.6]]


# calculations.process_coordinates(converted_track, len(track))

# float distanceBetweenPoints(float (*track)[2], int p1, int p2)
# def distance_between_points(track: list, p1, p2) -> float:
#     track = [[x, y] for x, y, *_ in track]

#     converted_track = (ctypes.c_float * 2 * len(track))()
#     for i, coord in enumerate(track):
#         for j, val in enumerate(coord):
#             converted_track[i][j] = ctypes.c_float(val)

#     return calculations.distanceBetweenPoints(converted_track, p1, p2)