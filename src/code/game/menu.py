from ..config import *
from ..manager import main_mgr, data
from random import randint


def hex_to_rgb(hex: str) -> pg.Color:
    hex = hex.removeprefix("#")
    rgb = []

    for i in (0, 2, 4):
        decimal = int(hex[i:i + 2], 16)
        rgb.append(decimal)

    return pg.Color(rgb)


THEMES: list[list] = [ # #222034
    ["#ac3232", "#8a1010", "#df6565", "#eeeeee"],
    ["#d77bba", "#a44887", "#faaffd", "#eeeeee"],
    ["#76428a", "#542068", "#a976bd", "#eeeeee"],
    ["#5b6ee1", "#394cc0", "#8e9ff4", "#eeeeee"],
    ["#306082", "#104060", "#6393b5", "#eeeeee"],
    ["#37946e", "#25724c", "#6ac79f", "#eeeeee"],
    ["#df7126", "#bd5004", "#ffb459", "#eeeeee"],
    ["#45283c", "#23061a", "#785b6f", "#eeeeee"]
]

# THEMES: list[list[pg.Color]] = [[] for _ in range(len(temp_THEMES))]

for n1, theme in enumerate(THEMES):
    for n2, color in enumerate(theme):
        THEMES[n1][n2] = hex_to_rgb(color)

THEME_CURRENT = randint(0, len(THEMES) - 1)

BACKGROUND_THEMED_MENU = pg.image.load(os.path.join("src", "textures", "backgrounds", f"background_{THEME_CURRENT + 1}.png")).convert()

SURF_MENU = pg.Surface((WIN_W, WIN_H), pg.SRCALPHA)


class Button:
    def __init__(self, text: str, feedback_id: int) -> None:
        self.text: str = text
        self.feedback_id: int = feedback_id

        self.color = THEMES[THEME_CURRENT][1]
        self.hover: int = 20

        temp_render: pg.Surface = FONT_5.render(text, True, "#222034")

        self.rect: pg.Rect = temp_render.get_rect()
        self.rect.x = WIN_W - temp_render.get_width()  - 20
        self.rect.y = WIN_H - temp_render.get_height() - 20 - FONT_5.get_height() * len(BUTTONS)

        del temp_render

    def draw(self) -> None:
        SURF_MENU.blit(FONT_5.render(self.text, True, self.color), self.rect)

    def update(self, MOUSE_POS: tuple[int, int], CLICKED_BUTTON: None | int) -> None | int:
        if self.hover < 20:
            self.color = [x + (((y - x) // (20)) * self.hover) for x, y in zip(THEMES[THEME_CURRENT][2], THEMES[THEME_CURRENT][1])]

        self.draw()

        if self.rect.collidepoint(MOUSE_POS):
            self.hover = max(0, self.hover - 1)

            if CLICKED_BUTTON == 1:
                return self.feedback_id
        else:
            self.hover = min(20, self.hover + 1)


BUTTONS: list[Button] = []


def menu_main(fade_in: bool = False) -> None | dict:
    BUTTONS.clear()
    BUTTONS.append(Button("Settings", 0))
    BUTTONS.append(Button("Career", 1))
    BUTTONS.append(Button("Custom race", 2))


    clock = pg.Clock()

    # Fade-in --------------------------------------
    if fade_in:
        fadein = pg.Surface((WIN_W, WIN_H))
        fadein.fill((0, 0, 0))

        for n in range(256).__reversed__():
            clock.tick(60 * 10)
            pg.event.pump()

            SURF_MENU.blit(BACKGROUND_THEMED_MENU, (0, 0))

            for button in BUTTONS:
                button.draw()

            fadein.set_alpha(n)

            WIN.blit(SURF_MENU, (0, 0))
            WIN.blit(fadein, (0, 0))

            pg.display.flip()

        del fadein, button
    # -------------------------------------- fade-in


    while 1:
        clock.tick(60)

        MOUSE_POS = pg.mouse.get_pos()
        CLICKED_BUTTON = None

        for e in pg.event.get():
            if e.type == pg.QUIT:
                pg.quit()
                exit()

            if e.type == pg.MOUSEBUTTONDOWN:
                CLICKED_BUTTON = e.button

        SURF_MENU.blit(BACKGROUND_THEMED_MENU, (0, 0))

        for button in BUTTONS:
            match button.update(MOUSE_POS, CLICKED_BUTTON):
                case 0:
                    return menu_settings()
                case 1:
                    return menu_career() # TODO - finish simulation first
                case 2:
                    return menu_custom_race()

        WIN.blit(SURF_MENU, (0, 0))
        pg.display.flip()

    return {}


def menu_settings() -> None:
    # IMG_ARROW_DOWN = pg.image.load(os.path.join("src", "textures", "buttons", "arrow.png")).convert_alpha()
    # IMG_ARROW_UP = pg.transform.rotate(IMG_ARROW_DOWN, 180).convert_alpha()

    # IMG_ARROW_DOWN.set_colorkey("#222034")
    # IMG_ARROW_UP.set_colorkey("#222034")


    BUTTONS.clear()
    # BUTTONS.append(Button("Start", 0))


    # ALL_TRACKS = main_mgr.show_all_tracks()

    # CATEGORIES_DICT = main_mgr.get_racing_categories_dict()
    # CATEGORIES_LIST = main_mgr.get_racing_categories_list()

    track_preview_surf       = pg.Surface((WIN_W - 20, 500),   pg.SRCALPHA)
    category_preview_surf    = pg.Surface((500,        500),   pg.SRCALPHA)
    other_settings_surf      = pg.Surface((500,        500),   pg.SRCALPHA)
    drivers_surf             = pg.Surface((500,        500),   pg.SRCALPHA)
    settings_background_surf = pg.Surface((WIN_W,      WIN_H), pg.SRCALPHA)

    settings_background_surf.set_alpha(40)

    # choosen_track = 0
    # CHOOSEN_RACING_CLASS: list[str] = ["Volo", "CAT-B"]

    # ALL_DRIVERS_LIST: list = main_mgr.ready_drivers(CHOOSEN_RACING_CLASS[0], CHOOSEN_RACING_CLASS[1])
    # CHOOSEN_DRIVERS_COUNT: int = len(ALL_DRIVERS_LIST)

    # OTHER_SETTINGS: dict[str, float] = {
    #     'race-length': 1
    # }

    # INCOMPATIBILIES: set[str] = set()

    # track_preview_arrow_next_rect = pg.Rect(500, 500 - 50 - 50,           50, 50)
    # track_preview_arrow_prev_rect = pg.Rect(500, 500 - 50 - 50 - 50 - 10, 50, 50)

    settings_background_render = FONT_6.render("Settings", True, THEMES[THEME_CURRENT][0])

    clock = pg.Clock()
    while 1:
        clock.tick(60)

        MOUSE_POS = pg.mouse.get_pos()
        CLICKED_BUTTON = None

        for e in pg.event.get():
            if e.type == pg.QUIT:
                pg.quit()
                exit()

            if e.type == pg.KEYDOWN:
                if e.key == pg.K_ESCAPE:
                    return

            if e.type == pg.MOUSEBUTTONDOWN:
                CLICKED_BUTTON = e.button


        # CURRENT_TRACK = main_mgr.track_show(ALL_TRACKS[choosen_track])
        # CURRENT_CLASS_MANIFEST = main_mgr.read_manifest(CHOOSEN_RACING_CLASS[0], CHOOSEN_RACING_CLASS[1])

        # if CURRENT_CLASS_MANIFEST['racing-type'] in CURRENT_TRACK:
        #     CURRENT_ALL_LAPS = int(max(1, (200_000 // CURRENT_TRACK[CURRENT_CLASS_MANIFEST['racing-type']]['info']['length'] + 1) * OTHER_SETTINGS['race-length']))


        SURF_MENU.blit(BACKGROUND_THEMED_MENU, (0, 0))

        settings_background_surf.fill((0, 0, 0, 0))
        for n in range(WIN_H // FONT_6.get_height()):
            settings_background_surf.blit(settings_background_render, (WIN_W -settings_background_render.get_width(), WIN_H - FONT_6.get_height() * (n + 1)))
            SURF_MENU.blit(settings_background_surf, (0, 0))


        category_preview_surf.fill((0, 0, 0, 0))
        track_preview_surf.fill((0, 0, 0, 0))
        other_settings_surf.fill((0, 0, 0, 0))
        drivers_surf.fill((0, 0, 0, 0))


        # Category preview -----------------------------------------------------------------------------------
        # _temp_category_preview_last_y = -FONT_4.get_height()
        # for racing_category in CATEGORIES_DICT:
        #     category_preview_surf.blit(FONT_4.render(racing_category, True, "azure"), (0, _temp_category_preview_last_y + FONT_4.get_height()))
        #     _temp_category_preview_last_y += FONT_4.get_height()

        #     for n, racing_class in enumerate(CATEGORIES_DICT[racing_category]):
        #         category_preview_surf.blit(FONT_2.render(racing_class, True, THEMES[THEME_CURRENT][0] if CHOOSEN_RACING_CLASS != None and CHOOSEN_RACING_CLASS[1] == racing_class else "azure2"), (20, _temp_category_preview_last_y + (FONT_4.get_height() * bool(not n)) + (FONT_2.get_height() * bool(n))))
        #         _temp_category_preview_last_y += (FONT_4.get_height() * bool(not n)) + (FONT_2.get_height() * bool(n))

        #         if pg.Rect(20, _temp_category_preview_last_y, 100, FONT_2.get_height()).collidepoint((MOUSE_POS[0] - 10, MOUSE_POS[1] - 500 - 10)) and (CLICKED_BUTTON == 1):
        #             CHOOSEN_RACING_CLASS = [racing_category, racing_class]
        #             ALL_DRIVERS_LIST: list = main_mgr.ready_drivers(CHOOSEN_RACING_CLASS[0], CHOOSEN_RACING_CLASS[1])
        #             CHOOSEN_DRIVERS_COUNT = len(ALL_DRIVERS_LIST)
        # ----------------------------------------------------------------------------------- category preview


        # Track preview --------------------------------------------------------------------------------------
        # track_preview_surf.blit(IMG_ARROW_DOWN, track_preview_arrow_next_rect)
        # track_preview_surf.blit(IMG_ARROW_UP,   track_preview_arrow_prev_rect)

        # if track_preview_arrow_next_rect.collidepoint((MOUSE_POS[0] - 10, MOUSE_POS[1] - 10)) and (CLICKED_BUTTON == 1):
        #     choosen_track += 1
        #     if choosen_track > len(ALL_TRACKS) - 1:
        #         choosen_track = 0

        # if track_preview_arrow_prev_rect.collidepoint((MOUSE_POS[0] - 10, MOUSE_POS[1] - 10)) and (CLICKED_BUTTON == 1):
        #     choosen_track -= 1
        #     if choosen_track < 0:
        #         choosen_track = len(ALL_TRACKS) - 1


        # track_preview_surf.blit(FONT_4.render(ALL_TRACKS[choosen_track], True, "azure"), (500, 0))

        # if CURRENT_CLASS_MANIFEST['racing-type'] in CURRENT_TRACK:
        #     track_preview_surf.blit(FONT_3.render("Lap length: " + str(round(CURRENT_TRACK[CURRENT_CLASS_MANIFEST['racing-type']]['info']['length'] / 1000, 3)) + " km", True, "azure"), (500, FONT_4.get_height()))

        #     if CURRENT_CLASS_MANIFEST['racing-type'] == "formula":
        #         track_preview_surf.blit(FONT_3.render("Laps: " + str(CURRENT_ALL_LAPS), True, "azure"), (500, FONT_4.get_height() + FONT_3.get_height()))

        #     track_preview_surf.blit(FONT_3.render("Race length: " + str(round(CURRENT_ALL_LAPS * CURRENT_TRACK[CURRENT_CLASS_MANIFEST['racing-type']]['info']['length'] / 1000, 3)) + " km", True, "azure"), (500, FONT_4.get_height() + FONT_3.get_height() + FONT_3.get_height()))


        # for racing_type in CURRENT_TRACK:
        #     if not racing_type in ["formula", "rallycross"]: continue
        #     pg.draw.lines(track_preview_surf, "white", True, main_mgr.scale_track_points([(x, y) for x, y, *_ in CURRENT_TRACK[racing_type]['track']], CURRENT_TRACK['scale']))
        # -------------------------------------------------------------------------------------- track preview


        # Other settings -------------------------------------------------------------------------------------
        # race_length_setting_render = FONT_3.render(f"Race length: {OTHER_SETTINGS['race-length'] * 100}%", True, "azure2")
        # race_length_setting_rect = pg.Rect(0, 0, race_length_setting_render.get_width(), race_length_setting_render.get_height())

        # other_settings_surf.blit(race_length_setting_render, race_length_setting_rect)

        # if race_length_setting_rect.collidepoint((MOUSE_POS[0] - 500 - 500 - 10, MOUSE_POS[1] - 500 - 10)) and (CLICKED_BUTTON == 1):
        #     match OTHER_SETTINGS['race-length']:
        #         case 1:
        #             OTHER_SETTINGS['race-length'] = 0.75
        #         case 0.75:
        #             OTHER_SETTINGS['race-length'] = 0.50
        #         case 0.5:
        #             OTHER_SETTINGS['race-length'] = 0.25
        #         case 0.25:
        #             OTHER_SETTINGS['race-length'] = 0.10
        #         case 0.1:
        #             OTHER_SETTINGS['race-length'] = 1.00
        # ------------------------------------------------------------------------------------- other settings


        # Drivers --------------------------------------------------------------------------------------------
        # for n, driver in enumerate(ALL_DRIVERS_LIST):
        #     if pg.Rect(0, FONT_2.get_height() * n, 500, FONT_2.get_height()).collidepoint((MOUSE_POS[0] - 500 - 10, MOUSE_POS[1] - 500 - 10)):
        #         if (CLICKED_BUTTON == 1):
        #             if n >= CHOOSEN_DRIVERS_COUNT:
        #                 ALL_DRIVERS_LIST.insert(0, driver)
        #                 ALL_DRIVERS_LIST.pop(n + 1)
        #                 CHOOSEN_DRIVERS_COUNT += 1
        #         elif (CLICKED_BUTTON == 3):
        #             if n < CHOOSEN_DRIVERS_COUNT:
        #                 ALL_DRIVERS_LIST.insert(CHOOSEN_DRIVERS_COUNT, driver)
        #                 ALL_DRIVERS_LIST.pop(n)
        #                 CHOOSEN_DRIVERS_COUNT -= 1

        #     if n < CHOOSEN_DRIVERS_COUNT:
        #         drivers_surf.blit(FONT_2.render(driver.full_name, True, "azure"), (0, FONT_2.get_height() * n))
        #     else:
        #         drivers_surf.blit(FONT_2.render(driver.full_name, True, THEMES[THEME_CURRENT][0]), (0, FONT_2.get_height() * n))
        # -------------------------------------------------------------------------------------------- drivers


        # Buttons --------------------------------------------------------------------------------------------
        # for button in BUTTONS:
        #     match button.update(MOUSE_POS, CLICKED_BUTTON):
        #         case 0:
        #             if not len(INCOMPATIBILIES):
        #                 return {"type": "custom-race", "category": CHOOSEN_RACING_CLASS[0], "class": CHOOSEN_RACING_CLASS[1], "track": ALL_TRACKS[choosen_track], "drivers": [d for n, d in enumerate(ALL_DRIVERS_LIST) if n < CHOOSEN_DRIVERS_COUNT], "laps": CURRENT_ALL_LAPS}
        # -------------------------------------------------------------------------------------------- buttons 


        # Incompatibilities ----------------------------------------------------------------------------------
        # INCOMPATIBILIES.clear()

        # if not CURRENT_CLASS_MANIFEST['racing-type'] in CURRENT_TRACK:
        #     INCOMPATIBILIES.add("This class is not allowed on this track")

        # if CHOOSEN_DRIVERS_COUNT <= 0:
        #     INCOMPATIBILIES.add("At least one driver must start")

        # for n, i in enumerate(INCOMPATIBILIES):
        #     SURF_MENU.blit(FONT_4.render(i, True, "red"), (10, WIN_H - FONT_4.get_height() * n - FONT_4.get_height()))
        # ---------------------------------------------------------------------------------- incompatibilities


        SURF_MENU.blit(track_preview_surf,    (0 + 10,         0 + 10))
        SURF_MENU.blit(category_preview_surf, (0 + 10,         500 + 10))
        SURF_MENU.blit(drivers_surf,          (500 + 10,       500 + 10))
        SURF_MENU.blit(other_settings_surf,   (500 + 500 + 10, 500 + 10))
        WIN.blit(SURF_MENU, (0, 0))
        pg.display.flip()


def menu_career() -> None | dict:
    # IMG_ARROW_DOWN = pg.image.load(os.path.join("src", "textures", "buttons", "arrow.png")).convert_alpha()
    # IMG_ARROW_UP = pg.transform.rotate(IMG_ARROW_DOWN, 180).convert_alpha()

    # IMG_ARROW_DOWN.set_colorkey("#222034")
    # IMG_ARROW_UP.set_colorkey("#222034")


    BUTTONS.clear()
    BUTTONS.append(Button("Start", 0))
    BUTTONS.append(Button("New career", 1))


    # ALL_TRACKS = main_mgr.show_all_tracks()

    # CATEGORIES_DICT = main_mgr.get_racing_categories_dict()
    # CATEGORIES_LIST = main_mgr.get_racing_categories_list()

    # track_preview_surf       = pg.Surface((WIN_W - 20, 500),   pg.SRCALPHA)
    # category_preview_surf    = pg.Surface((500,        500),   pg.SRCALPHA)
    # other_settings_surf      = pg.Surface((500,        500),   pg.SRCALPHA)
    # drivers_surf             = pg.Surface((500,        500),   pg.SRCALPHA)
    # settings_background_surf = pg.Surface((WIN_W,      WIN_H), pg.SRCALPHA)

    surf_career_list       = pg.Surface((500,   500),   pg.SRCALPHA)
    surf_career_background = pg.Surface((WIN_W, WIN_H), pg.SRCALPHA)

    surf_career_background.set_alpha(40)

    ALL_CAREERS = main_mgr.show_all_careers()

    CHOSEN_CAREER = 0

    # choosen_track = 0
    # CHOOSEN_RACING_CLASS: list[str] = ["Volo", "CAT-B"]

    # ALL_DRIVERS_LIST: list = main_mgr.ready_drivers(CHOOSEN_RACING_CLASS[0], CHOOSEN_RACING_CLASS[1])
    # CHOOSEN_DRIVERS_COUNT: int = len(ALL_DRIVERS_LIST)

    # OTHER_SETTINGS: dict[str, float] = {
    #     'race-length': 1
    # }

    # INCOMPATIBILIES: set[str] = set()

    # track_preview_arrow_next_rect = pg.Rect(500, 500 - 50 - 50,           50, 50)
    # track_preview_arrow_prev_rect = pg.Rect(500, 500 - 50 - 50 - 50 - 10, 50, 50)

    settings_background_render = FONT_6.render("Career", True, THEMES[THEME_CURRENT][0])

    clock = pg.Clock()
    while 1:
        clock.tick(60)

        MOUSE_POS = pg.mouse.get_pos()
        CLICKED_BUTTON = None

        for e in pg.event.get():
            if e.type == pg.QUIT:
                pg.quit()
                exit()

            if e.type == pg.KEYDOWN:
                if e.key == pg.K_ESCAPE:
                    return

            if e.type == pg.MOUSEBUTTONDOWN:
                CLICKED_BUTTON = e.button


        # CURRENT_TRACK = main_mgr.track_show(ALL_TRACKS[choosen_track])
        # CURRENT_CLASS_MANIFEST = main_mgr.read_manifest(CHOOSEN_RACING_CLASS[0], CHOOSEN_RACING_CLASS[1])

        # if CURRENT_CLASS_MANIFEST['racing-type'] in CURRENT_TRACK:
        #     CURRENT_ALL_LAPS = int(max(1, (200_000 // CURRENT_TRACK[CURRENT_CLASS_MANIFEST['racing-type']]['info']['length'] + 1) * OTHER_SETTINGS['race-length']))


        SURF_MENU.blit(BACKGROUND_THEMED_MENU, (0, 0))

        surf_career_background.fill((0, 0, 0, 0))
        for n in range(WIN_H // FONT_6.get_height()):
            surf_career_background.blit(settings_background_render, (WIN_W -settings_background_render.get_width(), WIN_H - FONT_6.get_height() * (n + 1)))
            SURF_MENU.blit(surf_career_background, (0, 0))


        surf_career_list.fill((0, 0, 0, 0))


        for button in BUTTONS:
            match button.update(MOUSE_POS, CLICKED_BUTTON):
                case 0:
                    pass
                case 1:
                    return sub_menu_career_new_career()


        # Career list ----------------------------------------------------------------------------------------
        for n, career in enumerate(ALL_CAREERS):
            if n == CHOSEN_CAREER:
                _temp_render_career = FONT_4.render(career, True, THEMES[THEME_CURRENT][0])
            else:
                _temp_render_career = FONT_4.render(career, True, "azure3")

            surf_career_list.blit(_temp_render_career, (0, FONT_4.get_height() * n))

            if pg.Rect(0, FONT_4.get_height() * n, _temp_render_career.get_width(), FONT_4.get_height()).collidepoint((MOUSE_POS[0] - 10, MOUSE_POS[1] - 10)) and (CLICKED_BUTTON == 1):
                CHOSEN_CAREER = n
        # ---------------------------------------------------------------------------------------- career list


        # Category preview -----------------------------------------------------------------------------------
        # _temp_category_preview_last_y = -FONT_4.get_height()
        # for racing_category in CATEGORIES_DICT:
        #     category_preview_surf.blit(FONT_4.render(racing_category, True, "azure"), (0, _temp_category_preview_last_y + FONT_4.get_height()))
        #     _temp_category_preview_last_y += FONT_4.get_height()

        #     for n, racing_class in enumerate(CATEGORIES_DICT[racing_category]):
        #         category_preview_surf.blit(FONT_2.render(racing_class, True, THEMES[THEME_CURRENT][0] if CHOOSEN_RACING_CLASS != None and CHOOSEN_RACING_CLASS[1] == racing_class else "azure2"), (20, _temp_category_preview_last_y + (FONT_4.get_height() * bool(not n)) + (FONT_2.get_height() * bool(n))))
        #         _temp_category_preview_last_y += (FONT_4.get_height() * bool(not n)) + (FONT_2.get_height() * bool(n))

        #         if pg.Rect(20, _temp_category_preview_last_y, 100, FONT_2.get_height()).collidepoint((MOUSE_POS[0] - 10, MOUSE_POS[1] - 500 - 10)) and (CLICKED_BUTTON == 1):
        #             CHOOSEN_RACING_CLASS = [racing_category, racing_class]
        #             ALL_DRIVERS_LIST: list = main_mgr.ready_drivers(CHOOSEN_RACING_CLASS[0], CHOOSEN_RACING_CLASS[1])
        #             CHOOSEN_DRIVERS_COUNT = len(ALL_DRIVERS_LIST)
        # ----------------------------------------------------------------------------------- category preview


        # Track preview --------------------------------------------------------------------------------------
        # track_preview_surf.blit(IMG_ARROW_DOWN, track_preview_arrow_next_rect)
        # track_preview_surf.blit(IMG_ARROW_UP,   track_preview_arrow_prev_rect)

        # if track_preview_arrow_next_rect.collidepoint((MOUSE_POS[0] - 10, MOUSE_POS[1] - 10)) and (CLICKED_BUTTON == 1):
        #     choosen_track += 1
        #     if choosen_track > len(ALL_TRACKS) - 1:
        #         choosen_track = 0

        # if track_preview_arrow_prev_rect.collidepoint((MOUSE_POS[0] - 10, MOUSE_POS[1] - 10)) and (CLICKED_BUTTON == 1):
        #     choosen_track -= 1
        #     if choosen_track < 0:
        #         choosen_track = len(ALL_TRACKS) - 1


        # track_preview_surf.blit(FONT_4.render(ALL_TRACKS[choosen_track], True, "azure"), (500, 0))

        # if CURRENT_CLASS_MANIFEST['racing-type'] in CURRENT_TRACK:
        #     track_preview_surf.blit(FONT_3.render("Lap length: " + str(round(CURRENT_TRACK[CURRENT_CLASS_MANIFEST['racing-type']]['info']['length'] / 1000, 3)) + " km", True, "azure"), (500, FONT_4.get_height()))

        #     if CURRENT_CLASS_MANIFEST['racing-type'] == "formula":
        #         track_preview_surf.blit(FONT_3.render("Laps: " + str(CURRENT_ALL_LAPS), True, "azure"), (500, FONT_4.get_height() + FONT_3.get_height()))

        #     track_preview_surf.blit(FONT_3.render("Race length: " + str(round(CURRENT_ALL_LAPS * CURRENT_TRACK[CURRENT_CLASS_MANIFEST['racing-type']]['info']['length'] / 1000, 3)) + " km", True, "azure"), (500, FONT_4.get_height() + FONT_3.get_height() + FONT_3.get_height()))


        # for racing_type in CURRENT_TRACK:
        #     if not racing_type in ["formula", "rallycross"]: continue
        #     pg.draw.lines(track_preview_surf, "white", True, main_mgr.scale_track_points([(x, y) for x, y, *_ in CURRENT_TRACK[racing_type]['track']], CURRENT_TRACK['scale']))
        # -------------------------------------------------------------------------------------- track preview


        # Other settings -------------------------------------------------------------------------------------
        # race_length_setting_render = FONT_3.render(f"Race length: {OTHER_SETTINGS['race-length'] * 100}%", True, "azure2")
        # race_length_setting_rect = pg.Rect(0, 0, race_length_setting_render.get_width(), race_length_setting_render.get_height())

        # other_settings_surf.blit(race_length_setting_render, race_length_setting_rect)

        # if race_length_setting_rect.collidepoint((MOUSE_POS[0] - 500 - 500 - 10, MOUSE_POS[1] - 500 - 10)) and (CLICKED_BUTTON == 1):
        #     match OTHER_SETTINGS['race-length']:
        #         case 1:
        #             OTHER_SETTINGS['race-length'] = 0.75
        #         case 0.75:
        #             OTHER_SETTINGS['race-length'] = 0.50
        #         case 0.5:
        #             OTHER_SETTINGS['race-length'] = 0.25
        #         case 0.25:
        #             OTHER_SETTINGS['race-length'] = 0.10
        #         case 0.1:
        #             OTHER_SETTINGS['race-length'] = 1.00
        # ------------------------------------------------------------------------------------- other settings


        # Drivers --------------------------------------------------------------------------------------------
        # for n, driver in enumerate(ALL_DRIVERS_LIST):
        #     if pg.Rect(0, FONT_2.get_height() * n, 500, FONT_2.get_height()).collidepoint((MOUSE_POS[0] - 500 - 10, MOUSE_POS[1] - 500 - 10)):
        #         if (CLICKED_BUTTON == 1):
        #             if n >= CHOOSEN_DRIVERS_COUNT:
        #                 ALL_DRIVERS_LIST.insert(0, driver)
        #                 ALL_DRIVERS_LIST.pop(n + 1)
        #                 CHOOSEN_DRIVERS_COUNT += 1
        #         elif (CLICKED_BUTTON == 3):
        #             if n < CHOOSEN_DRIVERS_COUNT:
        #                 ALL_DRIVERS_LIST.insert(CHOOSEN_DRIVERS_COUNT, driver)
        #                 ALL_DRIVERS_LIST.pop(n)
        #                 CHOOSEN_DRIVERS_COUNT -= 1

        #     if n < CHOOSEN_DRIVERS_COUNT:
        #         drivers_surf.blit(FONT_2.render(driver.full_name, True, "azure"), (0, FONT_2.get_height() * n))
        #     else:
        #         drivers_surf.blit(FONT_2.render(driver.full_name, True, THEMES[THEME_CURRENT][0]), (0, FONT_2.get_height() * n))
        # -------------------------------------------------------------------------------------------- drivers


        # Buttons --------------------------------------------------------------------------------------------
        # for button in BUTTONS:
        #     match button.update(MOUSE_POS, CLICKED_BUTTON):
        #         case 0:
        #             if not len(INCOMPATIBILIES):
        #                 return {"type": "custom-race", "category": CHOOSEN_RACING_CLASS[0], "class": CHOOSEN_RACING_CLASS[1], "track": ALL_TRACKS[choosen_track], "drivers": [d for n, d in enumerate(ALL_DRIVERS_LIST) if n < CHOOSEN_DRIVERS_COUNT], "laps": CURRENT_ALL_LAPS}
        # -------------------------------------------------------------------------------------------- buttons 


        # Incompatibilities ----------------------------------------------------------------------------------
        # INCOMPATIBILIES.clear()

        # if not CURRENT_CLASS_MANIFEST['racing-type'] in CURRENT_TRACK:
        #     INCOMPATIBILIES.add("This class is not allowed on this track")

        # if CHOOSEN_DRIVERS_COUNT <= 0:
        #     INCOMPATIBILIES.add("At least one driver must start")

        # for n, i in enumerate(INCOMPATIBILIES):
        #     SURF_MENU.blit(FONT_4.render(i, True, "red"), (10, WIN_H - FONT_4.get_height() * n - FONT_4.get_height()))
        # ---------------------------------------------------------------------------------- incompatibilities


        SURF_MENU.blit(surf_career_list, (0 + 10, 0 + 10))
        WIN.blit(SURF_MENU, (0, 0))
        pg.display.flip()


def sub_menu_career_new_career() -> None | dict:
    BUTTONS.clear()
    BUTTONS.append(Button("Start", 0))
    BUTTONS.append(Button("New career", 1))


    surf_team_picker           = pg.Surface((500, 500), pg.SRCALPHA)
    surf_new_career_background = pg.Surface((WIN_W, WIN_H), pg.SRCALPHA)

    surf_new_career_background.set_alpha(40)


    INCOMPATIBILIES: set[str] = set()

    settings_background_render = FONT_6.render("New career", True, THEMES[THEME_CURRENT][0])


    CAREER_FILE = data.default_career_file.copy()

    choosen_team = 0


    clock = pg.Clock()
    while 1:
        clock.tick(60)

        MOUSE_POS = pg.mouse.get_pos()
        CLICKED_BUTTON = None

        for e in pg.event.get():
            if e.type == pg.QUIT:
                pg.quit()
                exit()

            if e.type == pg.KEYDOWN:
                if e.key == pg.K_ESCAPE:
                    return

            if e.type == pg.MOUSEBUTTONDOWN:
                CLICKED_BUTTON = e.button


        SURF_MENU.blit(BACKGROUND_THEMED_MENU, (0, 0))

        surf_new_career_background.fill((0, 0, 0, 0))
        for n in range(WIN_H // FONT_6.get_height()):
            surf_new_career_background.blit(settings_background_render, (WIN_W -settings_background_render.get_width(), WIN_H - FONT_6.get_height() * (n + 1)))
            SURF_MENU.blit(surf_new_career_background, (0, 0))


        surf_team_picker.fill((0, 0, 0, 0))


        # Team picker ----------------------------------------------------------------------------------------
        for n, team in enumerate(data.teams):
            surf_team_picker.blit(FONT_4.render(team, True, THEMES[THEME_CURRENT][0] if choosen_team == n else "azure2"), (0, FONT_4.get_height() * n))
        # ---------------------------------------------------------------------------------------- team picker


        # Buttons --------------------------------------------------------------------------------------------
        for button in BUTTONS:
            match button.update(MOUSE_POS, CLICKED_BUTTON):
                case 0:
                    if not len(INCOMPATIBILIES):
                        return CAREER_FILE
        # -------------------------------------------------------------------------------------------- buttons 


        # Incompatibilities ----------------------------------------------------------------------------------
        INCOMPATIBILIES.clear()

        # if not CURRENT_CLASS_MANIFEST['racing-type'] in CURRENT_TRACK:
        #     INCOMPATIBILIES.add("This class is not allowed on this track")

        # if CHOOSEN_DRIVERS_COUNT <= 0:
        #     INCOMPATIBILIES.add("At least one driver must start")

        # for n, i in enumerate(INCOMPATIBILIES):
        #     SURF_MENU.blit(FONT_4.render(i, True, "red"), (10, WIN_H - FONT_4.get_height() * n - FONT_4.get_height()))
        # ---------------------------------------------------------------------------------- incompatibilities


        SURF_MENU.blit(surf_team_picker, (0 + 10, 0 + 10))
        WIN.blit(SURF_MENU, (0, 0))
        pg.display.flip()


def menu_custom_race():
    IMG_ARROW_DOWN = pg.image.load(os.path.join("src", "textures", "buttons", "arrow.png")).convert_alpha()
    IMG_ARROW_UP = pg.transform.rotate(IMG_ARROW_DOWN, 180).convert_alpha()

    IMG_ARROW_DOWN.set_colorkey("#222034")
    IMG_ARROW_UP.set_colorkey("#222034")


    BUTTONS.clear()
    BUTTONS.append(Button("Start", 0))


    ALL_TRACKS = main_mgr.show_all_tracks() # TODO - empty tracks dir

    CATEGORIES_DICT = main_mgr.get_racing_categories_dict()
    # CATEGORIES_LIST = main_mgr.get_racing_categories_list()

    track_preview_surf          = pg.Surface((WIN_W - 20, 500),   pg.SRCALPHA)
    category_preview_surf       = pg.Surface((500,        500),   pg.SRCALPHA)
    other_settings_surf         = pg.Surface((500,        500),   pg.SRCALPHA)
    drivers_surf                = pg.Surface((500,        500),   pg.SRCALPHA)
    custom_race_background_surf = pg.Surface((WIN_W,      WIN_H), pg.SRCALPHA)

    custom_race_background_surf.set_alpha(40)

    choosen_track = 0
    CHOOSEN_RACING_CLASS: list[str] = ["Volo", "CAT-B"]

    ALL_DRIVERS_LIST: list = main_mgr.ready_drivers(CHOOSEN_RACING_CLASS[0], CHOOSEN_RACING_CLASS[1])
    CHOOSEN_DRIVERS_COUNT: int = len(ALL_DRIVERS_LIST)

    OTHER_SETTINGS: dict[str, float] = {
        'race-length': 1
    }

    INCOMPATIBILIES: set[str] = set()

    track_preview_arrow_next_rect = pg.Rect(500, 500 - 50 - 50,           50, 50)
    track_preview_arrow_prev_rect = pg.Rect(500, 500 - 50 - 50 - 50 - 10, 50, 50)

    custom_race_background_render = FONT_6.render("Custom race", True, THEMES[THEME_CURRENT][0])

    clock = pg.Clock()
    while 1:
        clock.tick(60)

        MOUSE_POS = pg.mouse.get_pos()
        CLICKED_BUTTON = None

        for e in pg.event.get():
            if e.type == pg.QUIT:
                pg.quit()
                exit()

            if e.type == pg.KEYDOWN:
                if e.key == pg.K_ESCAPE:
                    return

            if e.type == pg.MOUSEBUTTONDOWN:
                CLICKED_BUTTON = e.button


        CURRENT_TRACK = main_mgr.track_show(ALL_TRACKS[choosen_track])
        CURRENT_CLASS_MANIFEST = main_mgr.read_manifest(CHOOSEN_RACING_CLASS[0], CHOOSEN_RACING_CLASS[1])

        if CURRENT_CLASS_MANIFEST['racing-type'] in CURRENT_TRACK:
            CURRENT_ALL_LAPS = int(max(1, (300_000 // CURRENT_TRACK[CURRENT_CLASS_MANIFEST['racing-type']]['info']['length'] + 1) * OTHER_SETTINGS['race-length']))


        SURF_MENU.blit(BACKGROUND_THEMED_MENU, (0, 0))

        custom_race_background_surf.fill((0, 0, 0, 0))
        for n in range(WIN_H // FONT_6.get_height()):
            custom_race_background_surf.blit(custom_race_background_render, (WIN_W -custom_race_background_render.get_width(), WIN_H - FONT_6.get_height() * (n + 1)))
            SURF_MENU.blit(custom_race_background_surf, (0, 0))


        category_preview_surf.fill((0, 0, 0, 0))
        track_preview_surf.fill((0, 0, 0, 0))
        other_settings_surf.fill((0, 0, 0, 0))
        drivers_surf.fill((0, 0, 0, 0))


        # Category preview -----------------------------------------------------------------------------------
        _temp_category_preview_last_y = -FONT_4.get_height()
        for racing_category in CATEGORIES_DICT:
            category_preview_surf.blit(FONT_4.render(racing_category, True, "azure"), (0, _temp_category_preview_last_y + FONT_4.get_height()))
            _temp_category_preview_last_y += FONT_4.get_height()

            for n, racing_class in enumerate(CATEGORIES_DICT[racing_category]):
                category_preview_surf.blit(FONT_2.render(racing_class, True, THEMES[THEME_CURRENT][0] if CHOOSEN_RACING_CLASS != None and CHOOSEN_RACING_CLASS[1] == racing_class else "azure2"), (20, _temp_category_preview_last_y + (FONT_4.get_height() * bool(not n)) + (FONT_2.get_height() * bool(n))))
                _temp_category_preview_last_y += (FONT_4.get_height() * bool(not n)) + (FONT_2.get_height() * bool(n))

                if pg.Rect(20, _temp_category_preview_last_y, 100, FONT_2.get_height()).collidepoint((MOUSE_POS[0] - 10, MOUSE_POS[1] - 500 - 10)) and (CLICKED_BUTTON == 1):
                    CHOOSEN_RACING_CLASS = [racing_category, racing_class]
                    ALL_DRIVERS_LIST: list = main_mgr.ready_drivers(CHOOSEN_RACING_CLASS[0], CHOOSEN_RACING_CLASS[1])
                    CHOOSEN_DRIVERS_COUNT = len(ALL_DRIVERS_LIST)
        # ----------------------------------------------------------------------------------- category preview


        # Track preview --------------------------------------------------------------------------------------
        track_preview_surf.blit(IMG_ARROW_DOWN, track_preview_arrow_next_rect)
        track_preview_surf.blit(IMG_ARROW_UP,   track_preview_arrow_prev_rect)

        if track_preview_arrow_next_rect.collidepoint((MOUSE_POS[0] - 10, MOUSE_POS[1] - 10)) and (CLICKED_BUTTON == 1):
            choosen_track += 1
            if choosen_track > len(ALL_TRACKS) - 1:
                choosen_track = 0

        if track_preview_arrow_prev_rect.collidepoint((MOUSE_POS[0] - 10, MOUSE_POS[1] - 10)) and (CLICKED_BUTTON == 1):
            choosen_track -= 1
            if choosen_track < 0:
                choosen_track = len(ALL_TRACKS) - 1


        track_preview_surf.blit(FONT_4.render(ALL_TRACKS[choosen_track], True, "azure"), (500, 0))

        if CURRENT_CLASS_MANIFEST['racing-type'] in CURRENT_TRACK:
            track_preview_surf.blit(FONT_3.render("Lap length: " + str(round(CURRENT_TRACK[CURRENT_CLASS_MANIFEST['racing-type']]['info']['length'] / 1000, 3)) + " km", True, "azure"), (500, FONT_4.get_height()))

            if CURRENT_CLASS_MANIFEST['racing-type'] == "formula":
                track_preview_surf.blit(FONT_3.render("Laps: " + str(CURRENT_ALL_LAPS), True, "azure"), (500, FONT_4.get_height() + FONT_3.get_height()))

            track_preview_surf.blit(FONT_3.render("Race length: " + str(round(CURRENT_ALL_LAPS * CURRENT_TRACK[CURRENT_CLASS_MANIFEST['racing-type']]['info']['length'] / 1000, 3)) + " km", True, "azure"), (500, FONT_4.get_height() + FONT_3.get_height() + FONT_3.get_height()))


        for racing_type in CURRENT_TRACK:
            if not racing_type in ["formula", "rallycross"]: continue
            pg.draw.lines(track_preview_surf, "white", True, main_mgr.scale_track_points([(x, y) for x, y, *_ in CURRENT_TRACK[racing_type]['track']], CURRENT_TRACK['scale']))
        # -------------------------------------------------------------------------------------- track preview


        # Other settings -------------------------------------------------------------------------------------
        race_length_setting_render = FONT_3.render(f"Race length: {OTHER_SETTINGS['race-length'] * 100}%", True, "azure2")
        race_length_setting_rect = pg.Rect(0, 0, race_length_setting_render.get_width(), race_length_setting_render.get_height())

        other_settings_surf.blit(race_length_setting_render, race_length_setting_rect)

        if race_length_setting_rect.collidepoint((MOUSE_POS[0] - 500 - 500 - 10, MOUSE_POS[1] - 500 - 10)) and (CLICKED_BUTTON == 1):
            match OTHER_SETTINGS['race-length']:
                case 1:
                    OTHER_SETTINGS['race-length'] = 0.75
                case 0.75:
                    OTHER_SETTINGS['race-length'] = 0.50
                case 0.5:
                    OTHER_SETTINGS['race-length'] = 0.25
                case 0.25:
                    OTHER_SETTINGS['race-length'] = 0.10
                case 0.1:
                    OTHER_SETTINGS['race-length'] = 1.00
        # ------------------------------------------------------------------------------------- other settings


        # Drivers --------------------------------------------------------------------------------------------
        for n, driver in enumerate(ALL_DRIVERS_LIST):
            if pg.Rect(0, FONT_2.get_height() * n, 500, FONT_2.get_height()).collidepoint((MOUSE_POS[0] - 500 - 10, MOUSE_POS[1] - 500 - 10)):
                if (CLICKED_BUTTON == 1):
                    if n >= CHOOSEN_DRIVERS_COUNT:
                        ALL_DRIVERS_LIST.insert(0, driver)
                        ALL_DRIVERS_LIST.pop(n + 1)
                        CHOOSEN_DRIVERS_COUNT += 1
                elif (CLICKED_BUTTON == 3):
                    if n < CHOOSEN_DRIVERS_COUNT:
                        ALL_DRIVERS_LIST.insert(CHOOSEN_DRIVERS_COUNT, driver)
                        ALL_DRIVERS_LIST.pop(n)
                        CHOOSEN_DRIVERS_COUNT -= 1

            if n < CHOOSEN_DRIVERS_COUNT:
                drivers_surf.blit(FONT_2.render(driver.full_name, True, THEMES[THEME_CURRENT][0]), (0, FONT_2.get_height() * n))
            else:
                drivers_surf.blit(FONT_2.render(driver.full_name, True, "azure3"), (0, FONT_2.get_height() * n))
        # -------------------------------------------------------------------------------------------- drivers


        # Buttons --------------------------------------------------------------------------------------------
        for button in BUTTONS:
            match button.update(MOUSE_POS, CLICKED_BUTTON):
                case 0:
                    if not len(INCOMPATIBILIES):
                        return {"type": "custom-race", "category": CHOOSEN_RACING_CLASS[0], "class": CHOOSEN_RACING_CLASS[1], "track": ALL_TRACKS[choosen_track], "drivers": [d for n, d in enumerate(ALL_DRIVERS_LIST) if n < CHOOSEN_DRIVERS_COUNT], "laps": CURRENT_ALL_LAPS}
        # -------------------------------------------------------------------------------------------- buttons 


        # Incompatibilities ----------------------------------------------------------------------------------
        INCOMPATIBILIES.clear()

        if not CURRENT_CLASS_MANIFEST['racing-type'] in CURRENT_TRACK:
            INCOMPATIBILIES.add("This class is not allowed on this track")

        if CHOOSEN_DRIVERS_COUNT <= 0:
            INCOMPATIBILIES.add("At least one driver must start")

        for n, i in enumerate(INCOMPATIBILIES):
            SURF_MENU.blit(FONT_4.render(i, True, "red"), (10, WIN_H - FONT_4.get_height() * n - FONT_4.get_height()))
        # ---------------------------------------------------------------------------------- incompatibilities


        SURF_MENU.blit(track_preview_surf,    (0 + 10,         0 + 10))
        SURF_MENU.blit(category_preview_surf, (0 + 10,         500 + 10))
        SURF_MENU.blit(drivers_surf,          (500 + 10,       500 + 10))
        SURF_MENU.blit(other_settings_surf,   (500 + 500 + 10, 500 + 10))
        WIN.blit(SURF_MENU, (0, 0))
        pg.display.flip()


def menu_confirm(text: str) -> bool:
    SURF_MENU = pg.Surface((WIN_W, WIN_H), pg.SRCALPHA)


    surf_background = pg.Surface((WIN_W, WIN_H), pg.SRCALPHA)
    surf_background.blit(WIN, (0, 0))

    # _temp_1_surf_background = pg.Surface((WIN_W, WIN_H), pg.SRCALPHA)
    _temp_2_surf_background = pg.Surface((WIN_W, WIN_H))

    # _temp_1_surf_background.fill(THEMES[THEME_CURRENT][0])

    _temp_2_surf_background.fill((0, 0, 0))
    _temp_2_surf_background.set_alpha(80)
    # _temp_2_surf_background.convert()

    # _temp_1_surf_background.blit(_temp_2_surf_background, (0, 0))
    # surf_background.blit(_temp_1_surf_background, (0, 0))

    # del _temp_1_surf_background, _temp_2_surf_background


    # from threading import Thread

    # _temp_surf_background = surf_background.copy()

    # _thread_blur = Thread(target=pg.transform.gaussian_blur, args=[surf_background.copy(), 16, False, surf_background], daemon=True)
    # _thread_blur.start()

    surf_background = pg.transform.gaussian_blur(surf_background, 2, False) # .convert()
    # surf_background = pg.transform.box_blur(surf_background, 16, False)


    render_text_color = "azure"
    render_text = FONT_4.render(text, True, render_text_color)
    render_text_rect = pg.Rect(WIN_W / 2 - render_text.get_width() / 2, WIN_H / 2 - render_text.get_height(), render_text.get_width(), render_text.get_height())

    render_no = FONT_5.render("No", True, "azure2")

    render_yes = FONT_5.render("Yes", True, "azure2")

    render_no_rect  = pg.Rect(WIN_W / 2 - render_no.get_width() - 20, WIN_H / 2, render_no.get_width(),  render_no.get_height())
    render_yes_rect = pg.Rect(WIN_W / 2                         + 20, WIN_H / 2, render_yes.get_width(), render_yes.get_height())


    clock = pg.Clock()
    while 1:
        clock.tick(60)

        MOUSE_POS = pg.mouse.get_pos()
        CLICKED_BUTTON = None

        for e in pg.event.get():
            if e.type == pg.QUIT:
                pg.quit()
                exit()

            if e.type == pg.KEYDOWN:
                if e.key == pg.K_ESCAPE:
                    return False

            if e.type == pg.MOUSEBUTTONDOWN:
                CLICKED_BUTTON = e.button


        SURF_MENU.fill((0, 0, 0))
        SURF_MENU.blit(surf_background, (0, 0))
        SURF_MENU.blit(_temp_2_surf_background, (0, 0))


        if render_no_rect.collidepoint(MOUSE_POS):
            render_no = FONT_4.render("No", True, THEMES[THEME_CURRENT][2])

            if CLICKED_BUTTON == 1:
                return False
        else:
            render_no = FONT_4.render("No", True, "azure4")

        if render_yes_rect.collidepoint(MOUSE_POS):
            render_yes = FONT_4.render("Yes", True, THEMES[THEME_CURRENT][2])

            if CLICKED_BUTTON == 1:
                return True
        else:
            render_yes = FONT_4.render("Yes", True, "azure4")


        SURF_MENU.blit(render_text, render_text_rect)
        SURF_MENU.blit(render_no,   render_no_rect)
        SURF_MENU.blit(render_yes,  render_yes_rect)


        WIN.blit(SURF_MENU, (0, 0))
        pg.display.flip()

    return False