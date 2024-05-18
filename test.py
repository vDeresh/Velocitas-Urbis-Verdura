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