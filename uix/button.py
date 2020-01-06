from typing import Union, Dict, Callable, Optional, List
from ..base.pyg_types import IntPoint
from .pyg_ctl import PygCtl
import pygame


GlobCaptureType = Union[dict, Callable[[pygame.event.EventType], bool], int, bool]


class Button(PygCtl):
    def __init__(self, lbl: str):
        super().__init__()
        self.lbl = lbl
        self.tot_rect: Optional[pygame.rect.RectType] = None
        self.glob_captures: Dict[int, GlobCaptureType] = {}

    def on_evt(self, app: "App", evt: pygame.event.EventType, pos: IntPoint) -> bool:
        if evt.type == pygame.MOUSEBUTTONDOWN:
            return self.on_mouse_down(app, evt)
        elif evt.type == pygame.MOUSEBUTTONUP:
            return self.on_mouse_up(app, evt)
        elif evt.type == pygame.KEYDOWN:
            return self.on_key_down(app, evt, pos)
        elif evt.type == pygame.KEYUP:
            return self.on_key_up(app, evt, pos)
        else:
            return False

    def add_glob_capture(self, evt_type: int, data: GlobCaptureType):
        self.glob_captures[evt_type] = data

    def rem_glob_capture(self, evt_type):
        if evt_type in self.glob_captures:
            del self.glob_captures[evt_type]

    def is_glob_capture(self, evt: pygame.event.EventType):
        if evt.type not in self.glob_captures:
            return False
        data = self.glob_captures[evt.type]
        if isinstance(data, dict):
            for k in data:
                if k.endswith("!&"):
                    k = k[:-2]
                    if getattr(evt, k) & data[k]:
                        return False
                elif k.endswith("&"):
                    k = k[:-1]
                    if (getattr(evt, k) & data[k]) == 0:
                        return False
                elif getattr(evt, k) != data[k]:
                    return False
            return True
        elif callable(data):
            return data(evt)
        elif isinstance(data, (bool, int)):
            return bool(data)
        else:
            return True

    def on_mouse_down(self, app: "App", evt: pygame.event.EventType) -> bool:
        return False

    def on_mouse_up(self, app: "App", evt: pygame.event.EventType) -> bool:
        return False

    def on_key_down(self, app: "App", evt: pygame.event.EventType, pos: IntPoint) -> bool:
        return False

    def on_key_up(self, app: "App", evt: pygame.event.EventType, pos: IntPoint):
        return False

    def collide_pt(self, pt: IntPoint) -> bool:
        return self.tot_rect is not None and self.tot_rect.collidepoint(pt[0], pt[1])

    def recalc_rect(self):
        pass

    def pre_draw(self, app: "App") -> List[pygame.rect.RectType]:
        if self.prev_rect is not None:
            return [app.draw_background_rect(self.prev_rect)]
        return []

    def set_lbl(self, app: "App", lbl: str):
        self.lbl = lbl
        self.recalc_rect()
        app.set_redraw(self)


from ..pyg_app import App
