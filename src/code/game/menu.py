from ..config import *
from ..manager import main_mgr
from random import randint


def hex_to_rgb(hex: str) -> pg.Color:
    hex = hex.removeprefix("#")
    rgb = []

    for i in (0, 2, 4):
        decimal = int(hex[i:i + 2], 16)
        rgb.append(decimal)

    return pg.Color(rgb)


THEMES: list[list] = [
    ["#ac3232", "#8a1010", "#eeeeee"],
    ["#d77bba", "#a44887", "#eeeeee"],
    ["#76428a", "#542068", "#eeeeee"],
    ["#5b6ee1", "#394cc0", "#eeeeee"],
    ["#306082", "#104060", "#eeeeee"],
    ["#37946e", "#25724c", "#eeeeee"],
    ["#df7126", "#bd5004", "#eeeeee"],
    ["#45283c", "#23061a", "#eeeeee"]
]

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
        self.hover: float = 20

        temp_render: pg.Surface = FONT_3.render(text, True, "#222034")

        self.rect: pg.Rect = temp_render.get_rect()
        self.rect.x = WIN_W - temp_render.get_width()  - 20
        self.rect.y = WIN_H - temp_render.get_height() - 20 - FONT_3.get_height() * len(BUTTONS)

        del temp_render

    def draw(self) -> None:
        SURF_MENU.blit(FONT_3.render(self.text, True, self.color), self.rect)

    def update(self, MOUSE_POS: tuple[int, int], CLICKED_BUTTON: None | int) -> None | int:
        if self.hover < 20:
            self.color = [x + (((y - x) / (20)) * self.hover) for x, y in zip(THEMES[THEME_CURRENT][2], THEMES[THEME_CURRENT][1])]

        self.draw()

        if self.rect.collidepoint(MOUSE_POS):
            self.hover = max(0, self.hover - 1)

            if CLICKED_BUTTON == 1:
                return self.feedback_id
        else:
            self.hover = min(20, self.hover + 1)


BUTTONS: list[Button] = []


def main_menu() -> dict:
    BUTTONS.clear()
    BUTTONS.append(Button("Settings", 0))
    BUTTONS.append(Button("Career", 1))
    BUTTONS.append(Button("Custom race", 2))


    # Drawing menu for fade-in -------------------
    
    # ------------------- drawing menu for fade-in


    clock = pg.Clock()

    # Fade-in --------------------------------------
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

    del fadein
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
                    pass
                case 1:
                    pass
                case 2:
                    _temp_custom_race = custom_race_menu()
                    if _temp_custom_race:
                        return _temp_custom_race
                    else:
                        pass

        WIN.blit(SURF_MENU, (0, 0))
        pg.display.flip()

    return {}


def custom_race_menu():
    BUTTONS.clear()
    BUTTONS.append(Button("Start", 0))


    ALL_TRACKS = main_mgr.show_all_tracks()

    CATEGORIES_DICT = main_mgr.get_racing_categories_dict()
    # CATEGORIES_LIST = main_mgr.get_racing_categories_list()

    track_preview_surf = pg.Surface((WIN_W - 20, 500), pg.SRCALPHA)
    category_preview_surf = pg.Surface((500, 500), pg.SRCALPHA)
    other_settings_surf = pg.Surface((500, 500), pg.SRCALPHA)
    drivers_surf = pg.Surface((500, 500), pg.SRCALPHA)

    choosen_track = 0
    CHOOSEN_RACING_CLASS: list[str] = ["Volo", "CAT-B"]

    ALL_DRIVERS_LIST: list = main_mgr.ready_drivers(CHOOSEN_RACING_CLASS[0], CHOOSEN_RACING_CLASS[1])
    CHOOSEN_DRIVERS_COUNT: int = len(ALL_DRIVERS_LIST)

    OTHER_SETTINGS = {
        'racing-type': "formula"
    }

    clock = pg.Clock()
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


        CURRENT_TRACK = main_mgr.track_show(ALL_TRACKS[choosen_track])


        SURF_MENU.blit(BACKGROUND_THEMED_MENU, (0, 0))

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
        track_preview_surf.blit(FONT_4.render(ALL_TRACKS[choosen_track], True, "azure"), (500, 0))

        for n, racing_type in enumerate(CURRENT_TRACK):
            if not racing_type in ["formula", "rallycross"]:
                continue

            pg.draw.lines(track_preview_surf, "white", True, main_mgr.scale_track_points([(x, y) for x, y, *_ in CURRENT_TRACK[racing_type]['track']], CURRENT_TRACK[racing_type]['info']['scale']))
        # -------------------------------------------------------------------------------------- track preview


        # Other settings -------------------------------------------------------------------------------------
        racing_type_setting_render = FONT_5.render(f"Racing type: {OTHER_SETTINGS['racing-type']}", True, "azure2")
        racing_type_setting_rect = pg.Rect(0, 0, racing_type_setting_render.get_width(), racing_type_setting_render.get_height())

        other_settings_surf.blit(racing_type_setting_render, racing_type_setting_rect)

        if racing_type_setting_rect.collidepoint((MOUSE_POS[0] - 500 - 10, MOUSE_POS[1] - 500 - 10)) and (CLICKED_BUTTON == 1):
            if OTHER_SETTINGS['racing-type'] == "formula":
                OTHER_SETTINGS['racing-type'] = "rallycross"
            elif OTHER_SETTINGS['racing-type'] == "rallycross":
                OTHER_SETTINGS['racing-type'] = "formula"
        # ------------------------------------------------------------------------------------- other settings


        # Drivers --------------------------------------------------------------------------------------------
        for n, driver in enumerate(ALL_DRIVERS_LIST):
            # pg.draw.circle(drivers_surf, "red", (MOUSE_POS[0] - 500 - 500 - 10, MOUSE_POS[1] - 500 - 10), 20)
            # pg.draw.rect(drivers_surf, "red", pg.Rect(0, FONT_2.get_height() * n, 500, FONT_2.get_height()))

            if pg.Rect(0, FONT_2.get_height() * n, 500, FONT_2.get_height()).collidepoint((MOUSE_POS[0] - 500 - 500 - 10, MOUSE_POS[1] - 500 - 10)):
                print(driver.full_name)
                if (CLICKED_BUTTON == 1):
                    if n >= CHOOSEN_DRIVERS_COUNT:
                        print("a")
                        ALL_DRIVERS_LIST.insert(0, driver)
                        ALL_DRIVERS_LIST.pop(n + 1)
                        CHOOSEN_DRIVERS_COUNT += 1
                elif (CLICKED_BUTTON == 3):
                    if n < CHOOSEN_DRIVERS_COUNT:
                        print("b")
                        ALL_DRIVERS_LIST.insert(CHOOSEN_DRIVERS_COUNT, driver)
                        ALL_DRIVERS_LIST.pop(n)
                        CHOOSEN_DRIVERS_COUNT -= 1

            if n < CHOOSEN_DRIVERS_COUNT:
                drivers_surf.blit(FONT_2.render(driver.full_name, True, "azure"), (0, FONT_2.get_height() * n))
            else:
                drivers_surf.blit(FONT_2.render(driver.full_name, True, THEMES[THEME_CURRENT][0]), (0, FONT_2.get_height() * n))
        # -------------------------------------------------------------------------------------------- drivers


        # Buttons --------------------------------------------------------------------------------------------
        for button in BUTTONS:
            match button.update(MOUSE_POS, CLICKED_BUTTON):
                case 0:
                    return {"type": "custom-race", "category": CHOOSEN_RACING_CLASS[0], "class": CHOOSEN_RACING_CLASS[1], "track": ALL_TRACKS[choosen_track], "racing-type": OTHER_SETTINGS['racing-type'], "drivers": [d for n, d in enumerate(ALL_DRIVERS_LIST) if n < CHOOSEN_DRIVERS_COUNT]}
        # -------------------------------------------------------------------------------------------- buttons 


        SURF_MENU.blit(track_preview_surf,    (0   + 10,       0   + 10))
        SURF_MENU.blit(category_preview_surf, (0   + 10,       500 + 10))
        SURF_MENU.blit(other_settings_surf,   (500 + 10,       500 + 10))
        SURF_MENU.blit(drivers_surf,          (500 + 500 + 10, 500 + 10))
        WIN.blit(SURF_MENU, (0, 0))
        pg.display.flip()