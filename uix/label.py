from typing import Optional, List
from ..base.pyg_types import Color, BgFgColor, IntPoint
from ..base.pyg_colors import WHITE
from .pyg_ctl import PygCtl
import pygame


antialias = False


X_ALIGN_LEFT = 0
X_ALIGN_MID = 1
X_ALIGN_RIGHT = 2
Y_ALIGN_TOP = 0
Y_ALIGN_MID = 4
Y_ALIGN_BOTTOM = 8
Y_ALIGN = 12
X_ALIGN = 3

ALIGN_LOW = 0
ALIGN_MID = 1
ALIGN_HIGH = 2


def calc_center(size: IntPoint, pos: IntPoint, center_w: int = 0, center_h: int = 0) -> pygame.rect.RectType:
    if center_w == ALIGN_LOW:
        pos_x = pos[0]
    elif center_w == ALIGN_MID:
        pos_x = pos[0] - size[0] // 2
    elif center_w == ALIGN_HIGH:
        pos_x = pos[0] - size[0]
    else:
        raise ValueError("Unrecognized center_w value")
    if center_h == ALIGN_LOW:
        pos_y = pos[1]
    elif center_h == ALIGN_MID:
        pos_y = pos[1] - size[1] // 2
    elif center_h == ALIGN_HIGH:
        pos_y = pos[1] - size[1]
    else:
        raise ValueError("Unrecognized center_h value")
    return pygame.rect.Rect((pos_x, pos_y), size)


class Label(PygCtl):
    # Centered is a bitwise combination of X_ALIGN and Y_ALIGN
    def __init__(self, lbl: str, pos: IntPoint, fnt: pygame.font.FontType, text_color: Color = WHITE,
                 bkgr_color: Optional[Color] = None, centered: int = 0):
        super().__init__()
        self.lbl = lbl
        self.fnt = fnt
        self.pos = pos
        self.text_color = text_color
        self.bkgr_color = bkgr_color
        self.centered = centered
        self.tot_rect = calc_center(
            fnt.size(lbl), self.pos,
            centered & X_ALIGN, (centered >> 2) & X_ALIGN
        )
        self.prev_rect = self.tot_rect
        self.aa = antialias

    def collide_pt(self, pt: IntPoint) -> bool:
        return self.tot_rect.collidepoint(pt[0], pt[1])

    def pre_draw(self, app: "App") -> List[pygame.rect.RectType]:
        if self.bkgr_color is None:
            return [app.draw_background_rect(self.prev_rect)]
        else:
            return [self.prev_rect]

    def draw(self, app):
        self.prev_rect = app.surf.blit(self.fnt.render(self.lbl, self.aa, self.text_color, self.bkgr_color), self.tot_rect)
        return [self.prev_rect]

    def set_lbl(self, app: "App",
                lbl: Optional[str],
                color: Optional[BgFgColor] = None,
                pos: Optional[IntPoint] = None,
                centered: Optional[int] = None):
        no_chg = 0
        if lbl is not None:
            self.lbl = lbl
        else:
            no_chg += 1
        if color is not None:
            self.bkgr_color, self.text_color = color
        else:
            no_chg += 1
        if pos is not None:
            self.pos = pos
        else:
            no_chg += 1
        if centered is not None:
            self.centered = centered
        else:
            no_chg += 1
        if no_chg >= 4:
            return
        self.lbl = lbl
        self.tot_rect = calc_center(
            self.fnt.size(self.lbl), self.pos,
            self.centered & X_ALIGN, (self.centered >> 2) & X_ALIGN
        )
        app.set_redraw(self)


from ..pyg_app import App
