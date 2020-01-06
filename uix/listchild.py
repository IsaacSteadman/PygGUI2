from typing import Optional
from ..utils.options import cache_imgs
from ..base.pyg_types import IntPoint
from .pyg_ctl import PygCtl
import pygame


class ListChild(PygCtl):
    def __init__(self, z_index: int):
        super().__init__()
        self.pos: Optional[IntPoint] = None
        self.z_index = z_index
        self.parent: Optional[ScrollBase] = None
        self.img: Optional[pygame.SurfaceType] = None
        self.is_show: bool = True
        self.coll_rect: Optional[pygame.rect.RectType] = None
        self.rel_pos: int = 0

    def hide(self, app: "App"):
        self.is_show = False
        app.set_redraw(self)
        try:
            app.ctls.remove(self)
        except ValueError:
            pass

    def on_evt(self, app: "App", evt: pygame.event.EventType, pos: IntPoint) -> bool:
        if evt.type == pygame.MOUSEBUTTONDOWN:
            if evt.button == 5:
                self.parent.scroll_down(app)
            elif evt.button == 4:  # Wheel rolled up
                self.parent.scroll_up(app)
            elif evt.button == 1 or evt.button == 3:  # left click
                if self.rel_pos == 0:  # selected
                    return self.click(app, evt)
                elif self.rel_pos > 0:
                    # self.parent.scroll_down()
                    return self.click(app, evt)
                elif self.rel_pos < 0:
                    # self.parent.scroll_up()
                    return self.click(app, evt)
        return False

    def click(self, app: "App", evt) -> bool:
        return False

    def show(self, app: "App"):
        self.is_show = True
        if not (self in app.ctls):
            app.ctls.insert(self.z_index, self)
        app.set_redraw(self)

    def draw(self, app: "App") -> List[pygame.rect.RectType]:
        if self.is_show and self.pos is not None:
            img = self.img
            if img is None:
                img = self.get_img()
            if cache_imgs:
                self.img = img
            else:
                self.img = None
            if img is None:
                return []
            self.prev_rect = app.surf.blit(img, self.pos)
            return [self.prev_rect]
        return []

    def pre_draw(self, app: "App") -> List[pygame.rect.RectType]:
        if self.prev_rect is not None:
            rtn = [app.draw_background_rect(self.prev_rect)]
            self.prev_rect = None
            return rtn
        return []

    def set_pos(self, app: "App", pos, index):
        self.pos = pos
        if self.is_show:
            app.set_redraw(self)
        self.rel_pos = index - self.parent.cur_pos
        self.coll_rect = pygame.rect.Rect(self.pos, self.get_size())

    def collide_pt(self, pt: IntPoint) -> bool:
        return self.coll_rect is not None and self.coll_rect.collidepoint(pt[0], pt[1])

    def get_size(self) -> IntPoint:
        try:
            return self.img.get_size()
        except AttributeError:
            return 0, 0

    def get_img(self) -> Optional[pygame.SurfaceType]:
        return None


from ..pyg_app import App
from .scrollbase import ScrollBase