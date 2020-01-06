from typing import Optional, List
from ..base.pyg_types import Color, BgFgColor, IntPoint
from ..base.pyg_colors import WHITE
from .pyg_ctl import PygCtl
import pygame


def calc_center(size: IntPoint, pos: IntPoint, center_w: bool = False, center_h: bool = False) -> pygame.rect.RectType:
    pos_x = pos[0] - (int(size[0] // 2) if center_w else 0)
    pos_y = pos[1] - (int(size[1] // 2) if center_h else 0)
    return pygame.rect.Rect((pos_x, pos_y), size)


class Label(PygCtl):
    # Centered
    #   0: not centered
    #   1: x centered
    #   2: y centered
    #   3: x and y centered
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
            bool(centered & 1), bool(centered & 2)
        )
        self.prev_rect = self.tot_rect

    def collide_pt(self, pt: IntPoint) -> bool:
        return self.tot_rect.collidepoint(pt[0], pt[1])

    def pre_draw(self, app: "App") -> List[pygame.rect.RectType]:
        if self.bkgr_color is None:
            return [app.draw_background_rect(self.prev_rect)]
        else:
            return [self.prev_rect]

    def draw(self, app):
        self.prev_rect = app.surf.blit(self.fnt.render(self.lbl, 0, self.text_color, self.bkgr_color), self.pos)
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
            bool(self.centered & 1), bool(self.centered & 2)
        )
        app.set_redraw(self)


from ..pyg_app import App