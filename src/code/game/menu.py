from ..config import *
from random import randint


def hex_to_rgb(hex: str) -> pg.Color:
    hex = hex.removeprefix("#")
    rgb = []

    for i in (0, 2, 4):
        decimal = int(hex[i:i + 2], 16)
        rgb.append(decimal)

    return pg.Color(rgb)


def main_menu() -> None:
    THEMES: list[list] = [
        ["#ac3232", "#8a1010", "#eeeeee"],
        ["#d77bba", "#b55998", "#eeeeee"],
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



    class Button:
        def __init__(self, text: str) -> None:
            self.text: str = text
            self.render: pg.Surface = FONT_3.render(text, True, "#222034")

            self.hover: float = 0

            self.rect: pg.Rect = self.render.get_rect()
            self.rect.x = WIN_W - self.render.get_width()  - 20
            self.rect.y = WIN_H - self.render.get_height() - 20 - FONT_3.get_height() * len(BUTTONS)

        def update(self, MOUSE_POS: tuple[int, int], CLICKED_BUTTON: None | int) -> None:
            if self.hover < 30:
                self.color = [x + (((y - x) / (30)) * self.hover) for x, y in zip(THEMES[THEME_CURRENT][0], THEMES[THEME_CURRENT][1])]


            if self.rect.collidepoint(MOUSE_POS):
                # self.color = THEMES[THEME_CURRENT][2]
                self.hover = min(30, self.hover - 1)

                if CLICKED_BUTTON == 1:
                    pass
            else:
                self.hover = max(0, self.hover + 1)
                # self.color = THEMES[THEME_CURRENT][1]


            self.render = FONT_3.render(self.text, True, self.color)

            SURF_MENU.blit(self.render, self.rect)


    BUTTONS: list[Button] = []
    BUTTONS.append(Button("Career"))
    BUTTONS.append(Button("Custom race"))



    BACKGROUND_THEMED_MENU = pg.image.load(os.path.join("src", "textures", "backgrounds", f"background_{THEME_CURRENT + 1}.png")).convert()

    SURF_MENU = pg.Surface((WIN_W, WIN_H), pg.SRCALPHA)

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
            button.update(MOUSE_POS, CLICKED_BUTTON)

        WIN.blit(SURF_MENU, (0, 0))
        pg.display.flip()