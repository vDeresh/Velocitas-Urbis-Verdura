import pygame as pg
import os


pg.display.init()
pg.font.init()

WIN_H = 1080 # 500
WIN_W = 1920 # 500
WIN = pg.display.set_mode((WIN_W, WIN_H), pg.SCALED | pg.FULLSCREEN)

# FPS = 60

# FONT_1 = pg.sysfont.SysFont("console", 24)
# FONT_2 = pg.sysfont.SysFont("console", 16)


FONT_1 = pg.Font(os.path.join("src", "fonts", "MajorMonoDisplay", "MajorMonoDisplay-Regular.ttf"), 16)
FONT_2 = pg.Font(os.path.join("src", "fonts", "RubikMonoOne", "RubikMonoOne-Regular.ttf"), 16)
FONT_3 = pg.Font(os.path.join("src", "fonts", "RubikMonoOne", "RubikMonoOne-Regular.ttf"), 24)
FONT_4 = pg.Font(os.path.join("src", "fonts", "RubikMonoOne", "RubikMonoOne-Regular.ttf"), 32)
FONT_5 = pg.Font(os.path.join("src", "fonts", "RubikMonoOne", "RubikMonoOne-Regular.ttf"), 64)
FONT_6 = pg.Font(os.path.join("src", "fonts", "RubikMonoOne", "RubikMonoOne-Regular.ttf"), 72)


COLOR_BACKGROUND = pg.Color(100, 110, 140)
COLOR_BACKGROUND_ALPHA_20 = pg.Color(100, 110, 140, 20)
COLOR_MONITOR = pg.Color(34, 32, 52)
COLOR_MONITOR_ALPHA_40 = pg.Color(34, 32, 52, 40)
COLOR_MONITOR_2 = pg.Color(26, 26, 44)
COLOR_MONITOR_2_ALPHA_40 = pg.Color(26, 26, 44, 40)


_const_simulation_speed = 240


# *** PROFILER RESULTS ***
# simulation (D:\Projekty\.python\.gry\Velocitas-Urbis-Verdura\src\code\game\racesim.py:34)
# function called 1 times

#          30190250 function calls (30085762 primitive calls) in 395.870 seconds

#    Ordered by: cumulative time, internal time, call count
#    List reduced from 138 to 40 due to restriction <40>

#    ncalls  tottime  percall  cumtime  percall filename:lineno(function)
# 6246/3619    0.809    0.000  541.968    0.150 queue.py:154(get)
#      9036   11.170    0.001  271.804    0.030 threading.py:323(wait)
# 65836/23748  171.759    0.003  170.684    0.007 {method 'tick' of 'pygame.time.Clock' objects}
#      2623    0.284    0.000  168.692    0.064 threading.py:637(wait)
#    477000  100.507    0.000  100.507    0.000 {method 'blit' of 'pygame.surface.Surface' objects}
#    843940   12.978    0.000   50.202    0.000 classes.py:134(update)
#     97272   17.360    0.000   17.360    0.000 {method 'fill' of 'pygame.surface.Surface' objects}
#   5319000   17.229    0.000   17.229    0.000 {built-in method pygame.draw.aalines}
#     23639   16.866    0.001   16.866    0.001 {built-in method pygame.display.flip}
#    843940    7.129    0.000   16.446    0.000 classes.py:110(calculate_speed)
#    842271    5.195    0.000    6.955    0.000 link.py:25(calculate_speed)
#    425460    1.271    0.000    3.878    0.000 classes.py:10(distance_to_next_driver)
#    497880    3.709    0.000    3.709    0.000 {method 'render' of 'pygame.font.Font' objects}
#    827576    2.610    0.000    2.766    0.000 classes.py:259(racing_logic)
#     42198    1.639    0.000    2.450    0.000 {method 'sort' of 'list' objects}
#    223407    2.058    0.000    2.439    0.000 others.py:5(distance_between_points)
#    969240    1.839    0.000    1.839    0.000 {built-in method pygame.draw.circle}
#     41718    1.068    0.000    1.479    0.000 {built-in method builtins.all}
#   7063684    1.231    0.000    1.231    0.000 {built-in method builtins.len}
#    842271    1.188    0.000    1.188    0.000 classes.py:86(gear)
#   3509732    0.926    0.000    0.926    0.000 {method 'distance_to' of 'pygame.math.Vector2' objects}
#   3257772    0.860    0.000    0.860    0.000 {method 'distance_squared_to' of 'pygame.math.Vector2' objects}
#    843940    0.594    0.000    0.810    0.000 racesim.py:80(<lambda>)
#    842271    0.509    0.000    0.558    0.000 classes.py:80(downforce)
#    843940    0.499    0.000    0.499    0.000 {method 'move_towards' of 'pygame.math.Vector2' objects}
#     58198    0.401    0.000    0.414    0.000 others.py:23(next_turn_data)
#     48522    0.411    0.000    0.411    0.000 racesim.py:82(<genexpr>)
#     23639    0.221    0.000    0.353    0.000 threading.py:1220(is_alive)
#     90320    0.250    0.000    0.329    0.000 link.py:41(calculate_tyre_wear)
#     23640    0.239    0.000    0.239    0.000 {built-in method pygame.event.get}
#      1312    0.057    0.000    0.137    0.000 pydevd.py:1681(process_internal_commands)
#    236105    0.134    0.000    0.134    0.000 {built-in method builtins.min}
#     23639    0.050    0.000    0.118    0.000 threading.py:1153(_wait_for_tstate_lock)
#    276407    0.075    0.000    0.075    0.000 {method 'random' of '_random.Random' objects}
#     36646    0.070    0.000    0.070    0.000 {built-in method builtins.round}
#      1312    0.009    0.000    0.068    0.000 pydevd.py:250(can_exit)
#    116349    0.064    0.000    0.064    0.000 {built-in method builtins.any}
#      9037    0.062    0.000    0.062    0.000 {built-in method _thread.allocate_lock}
#      1312    0.010    0.000    0.049    0.000 pydevd.py:1381(has_user_threads_alive)
#       2/1    0.064    0.032    0.048    0.048 racesim.py:34(simulation)