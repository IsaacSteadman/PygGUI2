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


def test_toggle_button():
    from .base.pyg_colors import RED, GREEN, WHITE, BLACK, BLUE
    from .pyg_app import App
    from .uix.togglebutton import ToggleButton
    import pygame
    pygame.display.init()
    pygame.font.init()
    fnt0 = pygame.font.SysFont("Courier New", 12)
    fnt1 = pygame.font.SysFont("Comic Sans", 12)
    fnt2 = pygame.font.SysFont("Times New Roman", 12)
    fnt3 = pygame.font.SysFont("Arial", 12)
    app = App(pygame.display.set_mode((640, 480)))
    act_fns = [
        lambda btn, pos: print("ACTION[0]: Toggle Button (%s) at position" % btn.lbl, pos),
        lambda btn, pos: print("ACTION[1]: Toggle Button (%s) at position" % btn.lbl, pos),
        lambda btn, pos: print("ACTION[2]: Toggle Button (%s) at position" % btn.lbl, pos)
    ]
    app.ctls.extend([
        ToggleButton("hello world [Courier New]", (160, 160), fnt0, lst_actions=act_fns),
        ToggleButton("hello world [Comic Sans]", (160, 180), fnt1, [(RED, WHITE), (GREEN, WHITE)], act_fns),
        ToggleButton("hello world 1 [Comic Sans]", (160, 200), fnt1, [(RED, WHITE), (GREEN, WHITE), (BLUE, WHITE)], act_fns),
        ToggleButton("hello world [Times New Roman]", (160, 220), fnt2, [(BLACK, RED), (BLACK, GREEN)], act_fns),
        ToggleButton("hello world [Arial]", (160, 240), fnt3, [(None, WHITE), (None, GREEN)], act_fns),
        ToggleButton("hello world 1 [Arial]", (160, 260), fnt3, [(None, WHITE), (None, GREEN), (None, BLUE)], act_fns),
        ToggleButton("hello world 2 [Comic Sans]", (160, 280), fnt1, [(GREEN, WHITE), (RED, WHITE)], act_fns)
    ])
    app.run()
    pygame.quit()


def test_entry_line():
    from .base.pyg_colors import RED, GREEN, WHITE, BLACK, BLUE
    from .pyg_app import App
    from .uix.entryline import EntryLine
    import pygame
    pygame.display.init()
    pygame.font.init()
    fnt0 = pygame.font.SysFont("Courier New", 12)
    fnt2 = pygame.font.SysFont("Times New Roman", 12)
    app = App(pygame.display.set_mode((640, 480)))
    act_fns = [
        lambda btn, pos: print("ACTION[0]: Toggle Button (%s) at position" % btn.lbl, pos),
        lambda btn, pos: print("ACTION[1]: Toggle Button (%s) at position" % btn.lbl, pos),
        lambda btn, pos: print("ACTION[2]: Toggle Button (%s) at position" % btn.lbl, pos)
    ]

    def pre_chg(el: EntryLine, evt):
        print("Pre change txt=%s, evt=%s" % (el.txt, evt))
        if evt.type == pygame.KEYDOWN and evt.key == pygame.K_r:
            print("blocked (char r)")
            return False
        return True

    def post_chg(el: EntryLine, evt):
        print("Post change txt=%s, evt=%s" % (el.txt, evt))

    def enter(el: EntryLine):
        print("Enter pressed txt=%s" % el.txt)

    EntryLine.init_timer(pygame.USEREVENT)

    # TODO: test conclusion
    # TODO:   it functionally works but there are some visual glitches
    # TODO:   if the EntryLine has a background color then it fails to clear out old text (erased by user)
    #           that has extended beyond the borders of the EntryLine
    # TODO:   if an EntryLine is deselected the text appears to get thicker with every cursor blink on another selected
    #           EntryLine
    # TODO: add some features
    #   CTRL+A - select all
    #   CTRL+Z and CTRL+SHIFT+Z - undo and redo
    #   Tab controls to go to next EntryLine/EntryBox
    #   key repeating

    el0 = EntryLine(
        fnt0, (160, 160), (160, 20), [GREEN, (64, 64, 64)],
        pre_chg, post_chg, enter, "hello [Courier New]"
    )

    el1 = EntryLine(
        fnt0, (160, 180), (160, 20), [WHITE, (64, 64, 64)],
        pre_chg, post_chg, enter, "hello [Courier New]"
    )

    el2 = EntryLine(
        fnt0, (160, 200), (160, 20), [WHITE],
        pre_chg, post_chg, enter, "hello [Courier New]"
    )

    el3 = EntryLine(
        fnt2, (160, 220), (160, 20), [GREEN, (64, 64, 64)],
        pre_chg, post_chg, enter, "hello [Times New Roman]"
    )

    el4 = EntryLine(
        fnt2, (160, 240), (160, 20), [WHITE, (64, 64, 64)],
        pre_chg, post_chg, enter, "hello [Times New Roman]"
    )

    el5 = EntryLine(
        fnt2, (160, 260), (160, 20), [WHITE],
        pre_chg, post_chg, enter, "hello [Times New Roman]"
    )
    app.ctls.extend([
        el0, el1, el2,
        el3, el4, el5
    ])
    app.run()
    pygame.quit()


def test_entry_box():
    from .base.pyg_colors import RED, GREEN, WHITE, BLACK, BLUE
    from .pyg_app import App
    from .uix.entrybox import EntryBox
    import pygame
    pygame.display.init()
    pygame.font.init()
    fnt0 = pygame.font.SysFont("Courier New", 12)
    fnt2 = pygame.font.SysFont("Times New Roman", 12)
    app = App(pygame.display.set_mode((640, 480)))
    act_fns = [
        lambda btn, pos: print("ACTION[0]: Toggle Button (%s) at position" % btn.lbl, pos),
        lambda btn, pos: print("ACTION[1]: Toggle Button (%s) at position" % btn.lbl, pos),
        lambda btn, pos: print("ACTION[2]: Toggle Button (%s) at position" % btn.lbl, pos)
    ]

    def pre_chg(el: EntryBox, evt):
        print("Pre change txt=%s, evt=%s" % (el.txt.string, evt))
        if evt.type == pygame.KEYDOWN and evt.key == pygame.K_r:
            print("blocked (char r)")
            return False
        return True

    def post_chg(el: EntryBox, evt):
        print("Post change txt=%s, evt=%s" % (el.txt.string, evt))

    def enter(el: EntryBox):
        print("Enter pressed txt=%s" % el.txt.string)

    EntryBox.init_timer(pygame.USEREVENT)

    # TODO: EntryBox functions but has all of the same problems as EntryLine

    eb0 = EntryBox(
        fnt0, (160, 40), (160, 160), [WHITE, (64, 64, 64)],
        pre_chg, post_chg, enter, "hello box [Courier New]"
    )

    eb1 = EntryBox(
        fnt0, (340, 40), (160, 160), [WHITE],
        pre_chg, post_chg, enter, "hello box [Courier New]"
    )

    eb2 = EntryBox(
        fnt2, (160, 240), (160, 160), [WHITE, (64, 64, 64)],
        pre_chg, post_chg, enter, "hello box [Times New Roman]"
    )

    eb3 = EntryBox(
        fnt2, (340, 240), (160, 160), [WHITE],
        pre_chg, post_chg, enter, "hello box [Times New Roman]"
    )
    app.ctls.extend([
        eb0,
        eb1,
        eb2,
        eb3
    ])
    app.run()
    pygame.quit()


if arg_data.test_name == "label":
    test_label()
elif arg_data.test_name == "press-button":
    test_press_button()
elif arg_data.test_name == "toggle-button":
    test_toggle_button()
elif arg_data.test_name == "entry-line":
    test_entry_line()
elif arg_data.test_name == "entry-box":
    test_entry_box()
else:
    print("Unrecognized test name '%s'" % arg_data.test_name)