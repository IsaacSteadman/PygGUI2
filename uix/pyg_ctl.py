import pygame
from typing import List, Tuple, Optional


class PygCtl(object):
    def __init__(self):
        self.prev_rect: Optional[pygame.rect.RectType] = None
        self.dirty: bool = False

    def draw(self, app: "App") -> List[pygame.rect.RectType]:
        return []

    def pre_draw(self, app: "App") -> List[pygame.rect.RectType]:
        return []

    def dirty_redraw(self, app: "App", lst_rects: List[pygame.rect.RectType]) -> List[pygame.rect.RectType]:
        if self.prev_rect is not None and self.prev_rect.collidelist(lst_rects):
            return self.draw(app)
        return []

    def on_evt(self, app: "App", evt: pygame.event.EventType, pos: Tuple[int, int]) -> bool:
        return False

    def on_evt_global(self, app: "App", evt: pygame.event.EventType) -> bool:
        return False

    def on_mouse_enter(self, app: "App") -> bool:
        return False

    def on_mouse_exit(self, app: "App") -> bool:
        return False

    def collide_pt(self, pt: Tuple[int, int]) -> bool:
        return False


from ..pyg_app import App
