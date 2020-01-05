from typing import Optional, List, Dict, Callable
from .uix.pyg_ctl import PygCtl
from .base.pyg_types import Point, Color, Number
import pygame


class App(object):
    def __init__(self):
        self.ctls: List[PygCtl] = []  # list of displayed controls
        self.redraw: List[PygCtl] = []  # list of controls that need to be redrawn
        self.surf: Optional[pygame.SurfaceType] = None  # pygame surface to use
        self.cur_pos: Point = (0, 0)
        self.cur_ctl: Optional[PygCtl] = None
        self.should_run: bool = True
        self.bkgr_surf: Optional[pygame.SurfaceType] = None
        self.bkgr_color: Color = (0, 0, 0)
        self.dct_global_event_func: Dict[int, Callable[[pygame.event.EventType], None]] = {}
        self.ask_exit: Optional[Callable[["App"], None]] = None
        self.chgd_pos = False
        self.used_time: Number = 0
        self.should_redraw: bool = False

    def exit(self):
        self.should_run = False

    def run(self):
        while self.should_run:
            pass

    def calc_collide(self):
        if self.cur_ctl is None or not self.cur_ctl.collide_pt(self.cur_pos):
            if self.cur_ctl is not None and self.cur_ctl.on_mouse_exit():
                self.set_redraw(self.cur_ctl)
            self.cur_ctl = None
            for ctl in self.ctls:
                if ctl.collide_pt(self.cur_pos):
                    if ctl.on_mouse_enter(self):
                        self.set_redraw(ctl)
                    self.cur_ctl = ctl
                    break
        elif self.cur_ctl is not None:
            pos = len(self.ctls)
            if self.cur_ctl in self.ctls:
                pos = self.ctls.index(self.cur_ctl)
            for c in range(pos):
                ctl = self.ctls[c]
                if ctl.collide_pt(self.cur_pos):
                    if self.cur_ctl.on_mouse_exit():
                        self.set_redraw(self.cur_ctl)
                    if ctl.on_mouse_enter(self):
                        self.set_redraw(ctl)
                    self.cur_ctl = ctl
                    break
            if not self.cur_ctl in self.ctls:
                self.cur_ctl = None
        return self.cur_ctl

    def process_event(self, evt: pygame.event.EventType):
        begin_time = pygame.time.get_ticks()
        if evt.type == pygame.VIDEORESIZE:
            if evt.type in self.dct_global_event_func:
                self.dct_global_event_func[evt.type](evt)
            self.surf = pygame.display.set_mode(evt.size, pygame.RESIZABLE)
            if self.bkgr_surf is None:
                self.surf.fill(self.bkgr_color)
            else:

                self.surf.blit(self.bkgr_surf, (0, 0))
            for ctl in self.ctls:
                ctl.on_evt_global(self, evt)
            for ctl in self.ctls:
                ctl.draw(self)
            pygame.display.update()
            self.used_time += pygame.time.get_ticks() - begin_time
            return
        ctl_evt_allow = True
        if evt.type == pygame.QUIT:
            if self.ask_exit is None:
                self.exit()
            else:
                self.ask_exit()
            return
        elif self.cur_ctl is not None and self.cur_ctl not in self.ctls:
            self.cur_ctl = None
            self.chgd_pos = False
            self.cur_ctl = self.calc_collide()
        elif self.chgd_pos:
            self.chgd_pos = False
            self.cur_ctl = self.calc_collide()
        if evt.type == pygame.MOUSEMOTION:
            self.cur_pos = evt.pos
            self.cur_ctl = self.calc_collide()
        elif evt.type in self.dct_global_event_func:
            ctl_evt_allow = False
            if not self.dct_global_event_func[evt.type](evt):
                return
        if ctl_evt_allow:
            if self.cur_ctl is not None and self.cur_ctl.on_evt(self, evt, self.cur_pos):
                self.set_redraw(self.cur_ctl)
            for ctl in self.ctls:
                if ctl.on_evt_global(self, evt):
                    self.set_redraw(ctl)
        if not self.should_redraw:
            return
        i = 0
        lst_cur_draw_removed = [
            ctl for ctl in self.redraw
            if ctl not in self.ctls
        ]
        self.redraw.clear()
        self.should_redraw = False
        pre_draw_rects = []
        for ctl in lst_cur_draw_removed:
            pre_draw_rects.extend(ctl.pre_draw(self))
        for ctl in self.ctls:
            if ctl.dirty:
                pre_draw_rects.extend(ctl.pre_draw(self))
        draw_rects = []
        for ctl in self.ctls:
            if ctl.dirty:
                draw_rects.extend(ctl.draw(self))
                ctl.dirty = False
            else:
                draw_rects.extend(ctl.dirty_redraw(self, pre_draw_rects))
        pre_draw_rects.extend(draw_rects)
        pygame.display.update(pre_draw_rects)
        self.used_time += pygame.time.get_ticks() - begin_time

    def set_redraw(self, ctl: PygCtl):
        self.redraw.append(ctl)
        ctl.dirty = True
        self.should_redraw = True

    @property
    def draw_bkgr_surf(self) -> bool:
        return self.bkgr_surf is not None

    def draw_background_lines(self, closed: bool, pts: List[Point], width: int) -> List[pygame.rect.RectType]:
        src = self.bkgr_surf
        tgt = self.surf
        if src is None:
            return [pygame.draw.lines(tgt, self.bkgr_color, closed, pts, width)]
        else:
            rects: List[Optional[pygame.rect.RectType]] = [None] * (len(pts) if closed else (len(pts) - 1))
            for i in range(len(pts) - 1):
                ax, ay = pts[i]
                bx, by = pts[i + 1]
                x = min(ax, bx)
                y = min(ay, by)
                dx = abs(ax - bx)
                dy = abs(ay - by)
                if width > 1:
                    x -= width - 1
                    y -= width - 1
                    dx += width - 1
                    dy += width - 1
                rects[i] = pygame.rect.Rect((x, y), (dx, dy))
            if closed:
                ax, ay = pts[0]
                bx, by = pts[-1]
                x = min(ax, bx)
                y = min(ay, by)
                dx = abs(ax - bx)
                dy = abs(ay - by)
                if width > 1:
                    x -= width - 1
                    y -= width - 1
                    dx += width - 1
                    dy += width - 1
                rects[-1] = pygame.rect.Rect((x, y), (dx, dy))
            tgt.blits([(src, rect, rect) for rect in rects])
            return rects

    def draw_background_rect(self, rect) -> pygame.rect.RectType:
        src = self.bkgr_surf
        tgt = self.surf
        if src is None:
            return tgt.fill(self.bkgr_color, rect)
        else:
            return tgt.blit(src, rect, rect)
