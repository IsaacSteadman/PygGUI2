from typing import List, Optional, Iterable, Callable
from ..base.pyg_types import Point, Number, Color
from .pyg_ctl import PygCtl
import pygame


def collide_pt_circle(pt_test: Point, pt_circle: Point, radius: Number) -> bool:
    off_x = pt_test[0] - pt_circle[0]
    off_y = pt_test[1] - pt_circle[1]
    return (off_x ** 2 + off_y ** 2) <= radius ** 2


def collide_line_width(pt_test: Point, pt1: Point, pt2: Point, width: Number) -> bool:
    if collide_pt_circle(pt_test, pt1, width) or collide_pt_circle(pt_test, pt2, width):
        return True
    x1 = pt1[0]
    x2 = pt2[0]
    if x1 > pt2[0]:
        x1 = pt2[0]
        x2 = pt1[0]
    y1 = pt1[1]
    y2 = pt2[1]
    if y1 > pt2[1]:
        y1 = pt2[1]
        y2 = pt1[1]
    the_rect = None
    if pt2[0] == pt1[0]:
        the_rect = pygame.rect.Rect(pt1[0] - width, y1, width * 2, y2 - y1)
    if pt2[1] == pt1[1]:
        the_rect = pygame.rect.Rect(x1, pt1[1] - width, x2 - x1, width * 2)
    if the_rect is not None:
        return the_rect.collidepoint(pt_test[0], pt_test[1])
    slope = (pt2[1] - pt1[1]) / (pt2[0] - pt1[0])
    m = slope + 1 / slope
    b1 = pt1[1] - pt1[0] * slope
    b2 = pt_test[1] + pt_test[0] / slope
    b = b1 - b2
    c_x = -b / m
    c_y = slope * c_x + b1
    if c_x < x1 or c_x > x2 or c_y < y1 or c_y > y2:
        return False
    return collide_pt_circle(pt_test, (c_x, c_y), width)


def get_euclid_dist(Pt1, Pt2):
    return ((Pt1[0] - Pt2[0]) ** 2 + (Pt1[1] - Pt2[1]) ** 2) ** .5


class Wire(PygCtl):
    def __init__(self, lst_pts: Iterable[Point], color: Color, act_func: Optional[Callable[[], None]] = None):
        super().__init__()
        self.lst_pts: List[Point] = list(lst_pts)
        self.color: Color = color
        self.width: int = 1  # width of line drawn
        self.prev_width: int = 1
        self.prev_lst_pts: Optional[List[Point]] = None
        self.m_width: int = 5  # width of mouse capture
        self.act_func = act_func

    def pre_draw(self, app):
        if self.prev_lst_pts is not None:
            return app.draw_background_lines(False, self.prev_lst_pts, self.prev_width)
        return []

    def draw(self, app):
        if len(self.lst_pts) < 2:
            return []
        self.prev_width = self.width
        self.prev_lst_pts = list(self.lst_pts)
        self.prev_rect = pygame.draw.lines(app.surf, self.color, False, self.lst_pts, self.width)
        return [self.prev_rect]

    def dirty_redraw(self, app, lst_rects):
        if self.prev_rect is not None and self.prev_rect.collidelist(lst_rects) == -1:
            return []
        rtn = []
        for c in range(len(self.lst_pts) - 1):
            x1 = self.lst_pts[c][0]
            y1 = self.lst_pts[c][1]
            x2 = self.lst_pts[c + 1][0]
            y2 = self.lst_pts[c + 1][1]
            if x2 < x1:
                xTmp = x2
                x2 = x1
                x1 = xTmp
            if y2 < y1:
                yTmp = y2
                y2 = y1
                y1 = yTmp
            lst_coll = pygame.rect.Rect(x1, y1, x2 - x1, y2 - y1).collidelistall(lst_rects)
            if len(lst_coll) > 0:
                new_rect = pygame.draw.line(app.surf, self.color, self.lst_pts[c], self.lst_pts[c + 1], self.width)
                for Index in lst_coll:
                    if lst_rects[Index].contains(new_rect): break
                else:
                    rtn.append(new_rect)
        return rtn

    def on_mouse_enter(self, app):
        self.width = 2
        return True

    def on_mouse_exit(self, app):
        self.width = 1
        return True

    def collide_pt(self, pt):
        if len(self.lst_pts) < 2: return False
        for c in range(len(self.lst_pts) - 1):
            if collide_line_width(pt, self.lst_pts[c], self.lst_pts[c + 1], self.m_width): return True
        return False

    def on_evt(self, app, evt, pos):
        if evt.type == pygame.MOUSEBUTTONDOWN and evt.button == 1:
            rtn = self.Cut(app, pos)
            if self.act_func is not None:
                self.act_func()
            return rtn
        else:
            return False

    def Cut(self, app, pt):
        cur_dist = 800
        cur_pt = None
        cur_pt_pos = -1
        for c in range(len(self.lst_pts)):
            find_pt = self.lst_pts[c]
            the_dist = get_euclid_dist(find_pt, pt)
            if the_dist < cur_dist:
                cur_pt = find_pt
                cur_dist = the_dist
                cur_pt_pos = c
        c = cur_pt_pos
        lst_new_pts = self.lst_pts[0:c - 1]
        lst_new_pts.append((self.lst_pts[c][0] - 3, self.lst_pts[c][1] + 10))
        self.lst_pts = self.lst_pts[c:]
        self.lst_pts[0] = (self.lst_pts[0][0] - 3, self.lst_pts[0][1] - 10)
        new_wire = Wire(lst_new_pts, self.color, self.act_func)
        app.ctls.append(new_wire)
        app.set_redraw(new_wire)
        return True