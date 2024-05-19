# import json

# while 1:
#     try:
#         with open("test", "r") as file:
#             json.load(file)
#         break
                            
#     except FileNotFoundError:
#         with open("test", "w") as file:
#             file.write("{}")

#     except json.decoder.JSONDecodeError:
#         with open("test", "w") as file:
#             file.write("{}")


from pygame import Vector2
from math import acos, sqrt, pi

vec1 = Vector2(0, 2)
vec2 = Vector2(0, -2)

dot = vec1.x * vec2.x + vec1.y * vec2.y

vm1 = sqrt((vec1.x * vec1.x) + (vec1.y * vec1.y))
vm2 = sqrt((vec2.x * vec2.x) + (vec2.y * vec2.y))

result = acos(dot / (vm1 * vm2))
result *= 180 / pi

print(result)