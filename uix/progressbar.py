from typing import List, Callable, Optional
from .pyg_ctl import PygCtl
from ..base.pyg_types import BgFgColor, Number, IntPoint
import pygame


class TooltipInfo(object):
    __slots__ = ["hover_fn", "fnt", "colors", "is_above"]

    def __init__(self, hover_fn: Callable[["ProgressBar", Number], str],
                 fnt: pygame.font.FontType, colors: BgFgColor, is_above: bool = True):
        self.hover_fn = hover_fn
        self.fnt = fnt
        self.colors = colors
        self.is_above = is_above


class ProgressBar(PygCtl):
    def __init__(self, pos: IntPoint, size: IntPoint, colors: BgFgColor,
                 act_fn: Optional[Callable[["ProgressBar", Number], None]] = None,
                 tooltip: Optional[TooltipInfo] = None, default_value: Number = 0):
        super().__init__()
        self.pos = pos
        self.size = size
        self.colors = colors
        self.act_fn = act_fn
        self.tooltip = tooltip
        self.value = default_value
        self.prev_rect = pygame.rect.Rect(self.pos, self.size)
        self.tooltip_img: Optional[pygame.SurfaceType] = None
        self.tooltip_rect: Optional[pygame.rect.RectType] = None
        self.tooltip_prev_rect: Optional[pygame.rect.RectType] = None

    def set_value(self, app: "App", value: Number):
        self.value = value
        app.set_redraw(self)

    def collide_pt(self, pt: IntPoint) -> bool:
        return self.prev_rect.collidepoint(pt[0], pt[1])

    def on_evt(self, app: "App", evt: pygame.event.EventType, pos: IntPoint) -> bool:
        if evt.type == pygame.MOUSEBUTTONDOWN and evt.button == 1:
            frac = (pos[0] - self.pos[0]) / self.size[0]
            self.act_fn(self, frac)
        elif evt.type == pygame.MOUSEMOTION:
            frac = (pos[0] - self.pos[0]) / self.size[0]
            if self.tooltip is not None:
                txt = self.tooltip.hover_fn(self, frac)
                img: pygame.SurfaceType = self.tooltip.fnt.render(txt, 1, self.tooltip.colors[1], self.tooltip.colors[0])
                tt_size = img.get_size()
                tt_x = pos[0] - tt_size[0] // 2
                tt_y = self.pos[1] - tt_size[1]
                self.tooltip_img = img
                self.tooltip_prev_rect = self.tooltip_rect
                self.tooltip_rect = pygame.rect.Rect((tt_x, tt_y), tt_size)
                return True
        return False

    def on_mouse_exit(self, app: "App") -> bool:
        self.tooltip_img = None
        self.tooltip_rect = None
        return True

    def draw(self, app: "App") -> List[pygame.rect.RectType]:
        bkgr_color, prog_color = self.colors
        if bkgr_color is not None:
            app.surf.fill(bkgr_color, self.prev_rect)
        width, height = self.size
        width = max(min(width, int(width * self.value)), 0)
        app.surf.fill(prog_color, pygame.rect.Rect(self.pos, (width, height)))
        rtn = [self.prev_rect]
        if self.tooltip_rect is not None:
            rtn.append(self.tooltip_rect)
            app.surf.blit(self.tooltip_img, self.tooltip_rect)
        return rtn

    def pre_draw(self, app: "App") -> List[pygame.rect.RectType]:
        rtn = [self.prev_rect]
        if self.tooltip_prev_rect is not None:
            rtn.append(self.tooltip_prev_rect)
            if self.tooltip.colors[0] is None or self.tooltip_rect is None or self.tooltip_rect != self.tooltip_prev_rect:
                app.draw_background_rect(self.tooltip_prev_rect)
            self.tooltip_prev_rect = self.tooltip_rect
        if self.colors[0] is None:
            app.draw_background_rect(self.prev_rect)
        return rtn


from ..pyg_app import App