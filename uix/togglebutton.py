from typing import List, Tuple, Optional, Callable, Iterable
from ..base.pyg_types import Point, Color, IntPoint, BgFgColor
from ..base.pyg_colors import WHITE, RED, GREEN
from .button import Button
import pygame


ActionType = Optional[Callable[["ToggleButton", Point], None]]


class ToggleButton(Button):
    def __init__(self, lbl: str, pos: IntPoint, fnt: pygame.font.FontType,
                 lst_colors: Iterable[BgFgColor] = ((RED, WHITE), (GREEN, WHITE)),
                 lst_actions: Iterable[ActionType] = (None, None),
                 default_state: int = 0):
        super().__init__(lbl)
        self.lst_colors: List[BgFgColor] = list(lst_colors)
        self.lst_actions: List[ActionType] = list(lst_actions)
        self.cur_state = default_state
        self.Pressed = False
        self.pos = pos
        self.fnt = fnt
        self.tot_rect = pygame.rect.Rect(pos, fnt.size(lbl))
        self.prev_rect = self.tot_rect

    def on_mouse_down(self, app: "App", evt: pygame.event.EventType) -> bool:
        if evt.button != 1:
            return False
        self.Pressed = True
        return False

    def on_mouse_up(self, app: "App", evt: pygame.event.EventType) -> bool:
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

    def on_evt_global(self, app: "App", evt: pygame.event.EventType) -> bool:
        if self.is_glob_capture(evt):
            self.Pressed = False
            self.cur_state += 1
            self.cur_state %= len(self.lst_colors)
            cur_act = self.lst_actions[self.cur_state]
            if cur_act is not None:
                cur_act(self, self.pos)
            return True

    def draw(self, app: "App") -> List[pygame.rect.RectType]:
        cur_color = self.lst_colors[self.cur_state]
        return [app.surf.blit(self.fnt.render(self.lbl, False, cur_color[1], cur_color[0]), self.pos)]

    def recalc_rect(self):
        self.prev_rect = self.tot_rect
        self.tot_rect = pygame.rect.Rect(self.pos, self.fnt.size(self.lbl))


from ..pyg_app import App