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

    def update(self, MOUSE_POS: tuple[int, int], CLICKED_BUTTON: None | int) -> None | int:
        if self.hover < 20:
            self.color = [x + (((y - x) / (20)) * self.hover) for x, y in zip(THEMES[THEME_CURRENT][2], THEMES[THEME_CURRENT][1])]

        SURF_MENU.blit(FONT_3.render(self.text, True, self.color), self.rect)

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

        SURF_MENU.blit(BACKGROUND_THEMED_MENU, (0, 0))

        for button in BUTTONS:
            match button.update(MOUSE_POS, CLICKED_BUTTON):
                case 0:
                    pass
                case 1:
                    pass
                case 2:
                    return {"type": "custom-race", "category": None, "class": None, "drivers": []}

        WIN.blit(SURF_MENU, (0, 0))
        pg.display.flip()

    return {}


def custom_race_menu():
    BUTTONS.clear()
    BUTTONS.append(Button("Start", 0))

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

        SURF_MENU.blit(BACKGROUND_THEMED_MENU, (0, 0))

        for button in BUTTONS:
            match button.update(MOUSE_POS, CLICKED_BUTTON):
                case 0:
                    pass
                case 1:
                    pass
                case 2:
                    return {"type": "custom-race", "category": None, "class": None, "drivers": []}

        WIN.blit(SURF_MENU, (0, 0))
        pg.display.flip()

    return {}