from typing import Optional, Callable
from ..base.pyg_types import Point, BgFgColor
from ..base.pyg_colors import WHITE, RED, GREEN
from ..utils.options import antialias
from .button import Button
import pygame


class PressButton(Button):
    def __init__(self, lbl: str, act_func: Optional[Callable[["PressButton", Point], None]],
                 pos: Point, fnt: pygame.font.FontType,
                 off_color: BgFgColor = (RED, WHITE),
                 on_color: BgFgColor = (GREEN, WHITE)):
        super().__init__(lbl)
        self.cur_st = False
        self.pos = pos
        self.fnt = fnt
        self.off_color = off_color
        self.on_color = on_color
        self.act_func = act_func
        self.tot_rect = pygame.rect.Rect(pos, fnt.size(lbl))
        self.prev_rect = self.tot_rect
        self.aa = antialias

    def on_mouse_down(self, app, evt):
        if evt.button != 1:
            return False
        self.cur_st = True
        return True

    def on_mouse_up(self, app, evt):
        if evt.button != 1:
            return False
        if not self.cur_st:
            return False
        self.cur_st = False
        if self.act_func is not None:
            self.act_func(self, evt.pos)
        return True

    def on_evt_global(self, app, evt):
        if self.cur_st and evt.type == pygame.MOUSEBUTTONUP and evt.button == 1:
            self.cur_st = False
            return True
        elif self.is_glob_capture(evt):
            self.cur_st = False
            if self.act_func is not None:
                self.act_func(self, self.pos)
            return True
        return False

    def draw(self, app):
        cur_color = self.off_color
        if self.cur_st:
            cur_color = self.on_color
        return [app.surf.blit(self.fnt.render(self.lbl, self.aa, cur_color[1], cur_color[0]), self.pos)]

    def recalc_rect(self):
        self.prev_rect = self.tot_rect
        self.tot_rect = pygame.rect.Rect(self.pos, self.fnt.size(self.lbl))
