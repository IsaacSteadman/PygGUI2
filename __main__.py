from sys import argv
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument("test_name")


arg_data = parser.parse_args()


def test_label():
    from .base.pyg_colors import RED, GREEN
    from .pyg_app import App
    from .uix.label import Label
    import pygame
    pygame.display.init()
    pygame.font.init()
    fnt0 = pygame.font.SysFont("Courier New", 12)
    fnt1 = pygame.font.SysFont("Comic Sans", 12)
    fnt2 = pygame.font.SysFont("Times New Roman", 12)
    fnt3 = pygame.font.SysFont("Arial", 12)
    app = App(pygame.display.set_mode((640, 480)))
    app.ctls.extend([
        Label("hello world [Courier New]", (160, 160), fnt0),
        Label("hello world [Comic Sans]", (160, 180), fnt1, RED),
        Label("hello world [Times New Roman]", (160, 200), fnt2, GREEN),
        Label("hello world [Arial]", (160, 220), fnt3)
    ])
    app.run()
    pygame.quit()


def test_press_button():
    from .base.pyg_colors import RED, GREEN, WHITE, BLACK
    from .pyg_app import App
    from .uix.pressbutton import PressButton
    import pygame
    pygame.display.init()
    pygame.font.init()
    fnt0 = pygame.font.SysFont("Courier New", 12)
    fnt1 = pygame.font.SysFont("Comic Sans", 12)
    fnt2 = pygame.font.SysFont("Times New Roman", 12)
    fnt3 = pygame.font.SysFont("Arial", 12)
    app = App(pygame.display.set_mode((640, 480)))
    act_fn = lambda btn, pos: print("ACTION[0]: Press button (%s) at position" % btn.lbl, pos)
    act_fn1 = lambda btn, pos: print("ACTION[1]: Press button (%s) at position" % btn.lbl, pos)
    app.ctls.extend([
        PressButton("hello world [Courier New]", act_fn, (160, 160), fnt0),
        PressButton("hello world [Comic Sans]", act_fn1, (160, 180), fnt1, (RED, WHITE), (GREEN, WHITE)),
        PressButton("hello world [Times New Roman]", act_fn1, (160, 200), fnt2, (BLACK, RED), (BLACK, GREEN)),
        PressButton("hello world [Arial]", act_fn, (160, 220), fnt3, (None, WHITE), (None, GREEN)),
        PressButton("hello world 2 [Comic Sans]", act_fn, (160, 240), fnt1, (GREEN, WHITE), (RED, WHITE))
    ])
    app.run()
    pygame.quit()


if arg_data.test_name == "label":
    test_label()
elif arg_data.test_name == "press-button":
    test_press_button()
elif arg_data.test_name == "toggle-button":
    test_toggle_button()
