from typing import Optional, List
from ..base.pyg_colors import WHITE
from ..base.pyg_types import Point
from .pyg_ctl import PygCtl
import pygame


class ScrollBase(PygCtl):
    # if anim_app is specified then scroll base will animate (update its child positions) immediately
    def __init__(self, lst_prn, n_disp, pos, spacing, anim_app: Optional["App"] = None, tick_event_id=pygame.USEREVENT):
        super().__init__()
        self.lst_prn: List[ListChild] = lst_prn
        for child in self.lst_prn:
            child.parent = self
        self.cur_pos = 0
        self.n_disp = n_disp
        self.real_pos = pos
        self.tick_event_id = tick_event_id
        self.line_color = WHITE
        pygame.time.set_timer(self.tick_event_id, 1000 / 20)
        off = .5
        if self.n_disp % 2 == 1:
            off = 1
        self.center = (self.n_disp - off) * spacing
        self.spacing = spacing
        self.tick = 0
        self.max_tick = 10
        self.width = 0
        for elem in lst_prn:
            elem_w = elem.get_size()[0]
            if elem_w > self.width:
                self.width = elem_w
        self.x_off_pos = 0
        self.n_disp = n_disp
        if spacing is not None:
            self.spacing = spacing
        start_off = (self.n_disp / 2) * self.spacing
        self.x_off_pos = self.get_elem_x_off(start_off - self.center)
        mid_off = self.get_elem_x_off(0)
        y_off_pos = (self.n_disp - self.n_disp % 2) * self.spacing / 2
        self.pos = (self.real_pos[0] - self.x_off_pos, self.real_pos[1] - y_off_pos)
        self.coll_rect = pygame.rect.Rect(self.real_pos[0], self.real_pos[1], self.width + (mid_off - self.x_off_pos),
                                          self.n_disp * self.spacing)
        if anim_app is not None:
            self.animate(anim_app)

    def get_elem_x_off(self, y_off_center):
        return 0

    def set_visual(self, n_disp, spacing=None):
        self.n_disp = n_disp
        if spacing is not None:
            self.spacing = spacing
        start_off = (self.n_disp / 2) * self.spacing
        self.x_off_pos = self.get_elem_x_off(start_off - self.center)
        mid_off = self.get_elem_x_off(0)
        y_off_pos = (self.n_disp - self.n_disp % 2) * self.spacing / 2
        self.pos = (self.real_pos[0] - self.x_off_pos, self.real_pos[1] - y_off_pos)
        self.coll_rect = pygame.rect.Rect(self.real_pos[0], self.real_pos[1], self.width + (mid_off - self.x_off_pos),
                                          self.n_disp * self.spacing)
        # print self.x_off_pos, mid_off, self.width

    def pre_draw(self, app):
        if self.prev_rect is not None:
            rtn = [app.draw_background_rect(self.prev_rect)]
            self.prev_rect = None
            return rtn
        return []

    def draw(self, app):
        # Fixes a problem with antialiased alpha blending ListChild instances
        #  Only a Temporary fix
        app.draw_background_rect(self.coll_rect)
        self.prev_rect = pygame.draw.rect(app.surf, self.line_color, self.coll_rect, 1)
        return [self.prev_rect]

    def on_evt_global(self, app, evt):
        if evt.type == self.tick_event_id:
            if self.tick == 0:
                return False
            elif self.tick > 0:
                self.tick -= 1
            elif self.tick < 0:
                self.tick += 1
            self.animate(app)
        return False

    def animate(self, app: "App"):
        start = self.cur_pos - self.n_disp / 2
        start_off = (self.n_disp / 2) * self.spacing + (self.tick * self.spacing / self.max_tick)
        if start < 0:
            start_off += -start * self.spacing
            start = 0
        end = self.cur_pos + (self.n_disp + 1) / 2
        if end > len(self.lst_prn):
            end = len(self.lst_prn)
        for c in range(max(0, start - self.n_disp), start):
            self.lst_prn[c].hide(app)
        for c in range(start, end):
            self.lst_prn[c].show(app)
            x_off_pos = self.get_elem_x_off(start_off - self.center)
            self.lst_prn[c].set_pos(app, (self.pos[0] + x_off_pos, start_off + self.pos[1]), c)
            start_off += self.spacing
        for c in range(end, min(len(self.lst_prn), end + self.n_disp)):
            self.lst_prn[c].hide(app)
        app.chgd_pos = True

    def collide_pt(self, pt: Point):
        return self.coll_rect.collidepoint(pt[0], pt[1])

    def on_evt(self, app, evt, pos):
        if evt.type == pygame.MOUSEBUTTONDOWN:
            if evt.button == 5:
                self.scroll_down(app)
            elif evt.button == 4:  # Wheel rolled up
                self.scroll_up(app)
        return False

    def scroll_down(self, app: "App"):
        if self.cur_pos < len(self.lst_prn) - 1:
            self.cur_pos += 1
            self.tick = self.max_tick
            self.animate(app)

    def scroll_up(self, app: "App"):
        if self.cur_pos > 0:
            self.cur_pos -= 1
            self.tick = -self.max_tick
            self.animate(app)


from ..pyg_app import App
from .listchild import ListChild