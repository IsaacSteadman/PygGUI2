from typing import List, Tuple, Optional, Callable
from ..base.pyg_types import Point, Color
from ..base.pyg_colors import WHITE, RED, GREEN
from .button import Button
import pygame


class ToggleButton(Button):
    def __init__(self, lbl: str, pos: Point, fnt: pygame.font.FontType,
                 lst_colors: List[Tuple[Optional[Color], Color]] = ((RED, WHITE), (GREEN, WHITE)),
                 lst_actions: List[Optional[Callable[["ToggleButton", Point], None]]] = (None, None),
                 default_state: int = 0):
        super().__init__(lbl)
        self.lst_colors = list(lst_colors)
        self.lst_actions = list(lst_actions)
        self.cur_state = default_state
        self.Pressed = False
        self.pos = pos
        self.fnt = fnt
        self.tot_rect = pygame.rect.Rect(pos, fnt.size(lbl))
        self.prev_rect = self.tot_rect

    def on_mouse_down(self, app, evt):
        if evt.button != 1:
            return False
        self.Pressed = True
        return False

    def on_mouse_up(self, app, evt):
        if evt.button != 1:
            return False
        if not self.Pressed:
            return False
        self.Pressed = False
        self.cur_state += 1
        self.cur_state %= len(self.lst_colors)
        cur_act = self.lst_actions[self.cur_state]
        if cur_act is not None:
            cur_act(self, evt.pos)
        return True

    def on_evt_global(self, app, evt):
        if self.is_glob_capture(evt):
            self.Pressed = False
            self.cur_state += 1
            self.cur_state %= len(self.lst_colors)
            cur_act = self.lst_actions[self.cur_state]
            if cur_act is not None:
                cur_act(self, self.pos)
            return True

    def draw(self, app):
        cur_color = self.lst_colors[self.cur_state]
        return [app.surf.blit(self.fnt.render(self.lbl, False, cur_color[1], cur_color[0]), self.pos)]

    def recalc_rect(self):
        self.prev_rect = self.tot_rect
        self.tot_rect = pygame.rect.Rect(self.pos, self.fnt.size(self.lbl))
