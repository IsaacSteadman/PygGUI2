from typing import Callable, Optional, List
from ..base.pyg_types import Color, Point
from ..utils.text import TextLineView
from ..utils.clipboard import PyperClipboard
from ..utils.misc import FuncListView, binary_approx
from .pyg_ctl import PygCtl
from .entryline import get_pos_in_kern, EntryLine, clipboard_types
import pygame


class EntryBox(PygCtl):
    cursor_timer_event_id = pygame.USEREVENT + 1
    # cursor threshold, the fraction of character width, height
    #  that represents border between 2 char positions
    cursor_thresh = (.5, 0.0)
    cursor = EntryLine.cursor

    @classmethod
    def init_timer(cls, evt_code: int = None):
        if evt_code is not None:
            cls.cursor_timer_event_id = evt_code
        pygame.time.set_timer(cls.cursor_timer_event_id, 500)
        cls.clipboard = PyperClipboard()  # PygClipboard()

    def __init__(self, fnt: pygame.font.FontType, pos: Point, size: Point, colors: List[Color],
                 pre_chg: Optional[Callable[["EntryBox", pygame.event.EventType], bool]] = None,
                 post_chg: Optional[Callable[["EntryBox", pygame.event.EventType], None]] = None,
                 enter: Optional[Callable[["EntryBox"], None]] = None,
                 default_text: str = "",
                 censor: Optional[Callable[[str], str]] = None):
        super().__init__()
        self.line_sep = "\n"
        self.colors = colors
        self.highlight_colors: List[Color] = [(255, 255, 255), (51, 143, 255)]
        self.pos = pos
        self.size = size
        self.pre_chg = pre_chg
        self.post_chg = post_chg
        self.enter = enter
        self.censor = censor
        self.is_selected: bool = False
        self.highlight: bool = False
        self.highlight_pos: List[int] = [0, 0]
        self.txt = TextLineView(default_text, self.line_sep)
        self.ch_pos: List[int] = [0, 0]
        self.ch_off: int = 0  # x offset in pixels
        self.cur_key = None
        self.coll_rect: pygame.rect.RectType = pygame.rect.Rect(self.pos, self.size)
        self.prev_rect = self.coll_rect
        self.fnt = fnt
        self.cursor_state: bool = True
        self.cursor_col: Optional[int] = None
        self.line_h: int = fnt.get_linesize()
        self.old_cursor: Optional[tuple] = None

    def set_size(self, size):
        self.size = size
        self.coll_rect = pygame.rect.Rect(self.pos, self.size)

    def set_pos(self, pos):
        self.pos = pos
        self.coll_rect = pygame.rect.Rect(self.pos, self.size)

    def set_pos_size(self, pos, size):
        self.pos = pos
        self.size = size
        self.coll_rect = pygame.rect.Rect(self.pos, self.size)

    def on_evt(self, app, evt, pos):
        if evt.type == pygame.MOUSEBUTTONDOWN:
            self.highlight = True
            self.is_selected = True
            pos = [pos[0] - self.pos[0], pos[1] - self.pos[1]]
            if pos[0] < 0:
                pos[0] = 0
            if pos[1] < 0:
                pos[1] = 0
            cursor_thresh_x, cursor_thresh_y = EntryBox.cursor_thresh
            ch_row = max(0, min(int(pos[1] / self.line_h + cursor_thresh_y), len(self.txt.lines) - 1))
            draw_txt = self.txt.get_draw_row(ch_row)
            if self.censor is not None:
                draw_txt = self.censor(draw_txt)

            def get_size_text(x):
                return self.fnt.size(draw_txt[:x])[0]

            lst_v = FuncListView(get_size_text, len(draw_txt))
            # since lst_v[0] == 0 and pos[0] >= 0 is True, result->ch_pos >= 1
            ch_col = binary_approx(lst_v, pos[0])
            if ch_col < len(lst_v):
                off_x = lst_v[ch_col - 1]
                ch_w = lst_v[ch_col] - off_x
                if pos[0] - off_x <= cursor_thresh_x * ch_w:
                    ch_col -= 1
            self.ch_pos = [ch_col, ch_row]
            self.highlight_pos = [ch_col, ch_row]
            return True
        return False

    def on_pre_chg(self, evt):
        return self.pre_chg is None or self.pre_chg(self, evt)

    def on_mouse_enter(self, app):
        if pygame.mouse.get_cursor() != self.cursor:
            self.old_cursor = pygame.mouse.get_cursor()
            pygame.mouse.set_cursor(*self.cursor)
        return super().on_mouse_enter(app)

    def on_mouse_exit(self, app):
        if self.old_cursor is not None:
            pygame.mouse.set_cursor(*self.old_cursor)
            self.old_cursor = None
        return super().on_mouse_exit(app)

    def on_evt_global(self, app, evt):
        if evt.type == pygame.MOUSEBUTTONDOWN:
            if self.coll_rect.collidepoint(evt.pos[0], evt.pos[1]):
                return False
            if self.highlight or self.is_selected:
                self.highlight = False
                self.is_selected = False
        elif evt.type == pygame.MOUSEBUTTONUP:
            if self.highlight:
                self.highlight = False
        elif evt.type == pygame.MOUSEMOTION and self.highlight:
            pos = evt.pos
            pos = [pos[0] - self.pos[0], pos[1] - self.pos[1]]
            if pos[0] < 0:
                pos[0] = 0
            if pos[1] < 0:
                pos[1] = 0
            cursor_thresh_x, cursor_thresh_y = EntryBox.cursor_thresh
            ch_row = max(0, min(int(pos[1] / self.line_h + cursor_thresh_y), len(self.txt.lines) - 1))
            draw_txt = self.txt.get_draw_row(ch_row)
            if self.censor is not None:
                draw_txt = self.censor(draw_txt)

            def get_size_text(x):
                return self.fnt.size(draw_txt[:x])[0]

            lst_v = FuncListView(get_size_text, len(draw_txt))
            # since lst_v[0] == 0 and pos[0] >= 0 is True, result->ch_pos >= 1
            ch_col = binary_approx(lst_v, pos[0])
            if ch_col < len(lst_v):
                off_x = lst_v[ch_col - 1]
                ch_w = lst_v[ch_col] - off_x
                if pos[0] - off_x <= cursor_thresh_x * ch_w:
                    ch_col -= 1
            self.ch_pos = [ch_col, ch_row]
            return True
        elif evt.type == pygame.KEYDOWN and self.is_selected:
            is_chg = False
            ch_pos = self.txt.row_col_to_pos(*self.ch_pos)
            col_chg = True
            if evt.key == pygame.K_BACKSPACE:
                if ch_pos == 0 and self.ch_pos == self.highlight_pos or not self.on_pre_chg(evt):
                    return False
                elif evt.mod & pygame.KMOD_CTRL > 0:
                    start = EntryLine.prev_word(self.txt.string, ch_pos)
                    off = ch_pos - start
                    highlight_pos = self.txt.row_col_to_pos(*self.highlight_pos)
                    self.txt.delete(start, ch_pos)
                    if highlight_pos >= ch_pos:
                        highlight_pos -= off
                    elif highlight_pos > ch_pos - off:
                        highlight_pos = ch_pos
                    ch_pos = start
                    self.ch_pos = self.txt.pos_to_row_col(ch_pos)
                    self.highlight_pos = self.txt.pos_to_row_col(highlight_pos)
                    is_chg = True
                else:
                    if self.ch_pos != self.highlight_pos:
                        start, end = sorted((ch_pos, self.txt.row_col_to_pos(*self.highlight_pos)))
                        self.txt.delete(start, end)
                        self.ch_pos = self.txt.pos_to_row_col(start)
                        is_chg = True
                    else:
                        if ch_pos > 0:
                            self.txt.delete(ch_pos - 1, ch_pos)
                            self.ch_pos = self.txt.pos_to_row_col(ch_pos - 1)
                            is_chg = True
                    self.highlight_pos = list(self.ch_pos)
            elif evt.key == pygame.K_RETURN and evt.mod & pygame.KMOD_CTRL:
                if self.enter is not None:
                    self.enter(self)
            elif evt.key == pygame.K_DELETE:
                if (ch_pos >= len(self.txt.string) and self.ch_pos == self.highlight_pos) or not self.on_pre_chg(evt):
                    return False
                elif evt.mod & pygame.KMOD_CTRL > 0:
                    end = EntryLine.next_word(self.txt.string, ch_pos)
                    off = end - ch_pos
                    highlight_pos = self.txt.row_col_to_pos(*self.highlight_pos)
                    self.txt.delete(ch_pos, end)
                    if highlight_pos > ch_pos:
                        self.highlight_pos = self.txt.pos_to_row_col(max(highlight_pos - off, ch_pos))
                    is_chg = True
                else:
                    if self.ch_pos != self.highlight_pos:
                        start, end = sorted((ch_pos, self.txt.row_col_to_pos(*self.highlight_pos)))
                        self.txt.delete(start, end)
                        self.ch_pos = self.txt.pos_to_row_col(start)
                        is_chg = True
                    else:
                        if ch_pos < len(self.txt.string):
                            self.txt.delete(ch_pos, ch_pos + 1)
                            is_chg = True
                    self.highlight_pos = list(self.ch_pos)
            elif evt.key == pygame.K_HOME:
                if evt.mod & pygame.KMOD_CTRL > 0:
                    self.ch_pos[1] = 0
                self.ch_pos[0] = 0
                if evt.mod & pygame.KMOD_SHIFT == 0:
                    self.highlight_pos = list(self.ch_pos)
            elif evt.key == pygame.K_END:
                if evt.mod & pygame.KMOD_CTRL > 0:
                    self.ch_pos[1] = len(self.txt.lines) - 1
                self.ch_pos[0] = self.txt.get_draw_row_len(self.ch_pos[1])
                if evt.mod & pygame.KMOD_SHIFT == 0:
                    self.highlight_pos = list(self.ch_pos)
            elif evt.key == pygame.K_RETURN:
                # if self.enter is not None:
                # self.enter(self)
                self.txt.replace(self.line_sep, *sorted([ch_pos, self.txt.t_row_col_to_pos(self.highlight_pos)]))
                self.ch_pos[0] = 0
                self.ch_pos[1] += 1
                is_chg = True
                self.highlight_pos = list(self.ch_pos)
            elif evt.key == pygame.K_LEFT:
                if evt.mod & pygame.KMOD_CTRL > 0:
                    self.ch_pos = self.txt.pos_to_row_col(EntryLine.prev_word(self.txt.string, ch_pos))
                elif ch_pos > 0:
                    if evt.mod & pygame.KMOD_SHIFT == 0 and self.ch_pos != self.highlight_pos:
                        start, end = sorted((ch_pos, self.txt.row_col_to_pos(*self.highlight_pos)))
                        self.ch_pos = self.txt.pos_to_row_col(start)
                    else:
                        self.ch_pos = self.txt.pos_to_row_col(ch_pos - 1)
                if evt.mod & pygame.KMOD_SHIFT == 0:
                    self.highlight_pos = list(self.ch_pos)
            elif evt.key == pygame.K_RIGHT:
                if evt.mod & pygame.KMOD_CTRL > 0:
                    self.ch_pos = self.txt.pos_to_row_col(EntryLine.next_word(self.txt.string, ch_pos))
                elif ch_pos < len(self.txt.string):
                    if evt.mod & pygame.KMOD_SHIFT == 0 and self.ch_pos != self.highlight_pos:
                        start, end = sorted((ch_pos, self.txt.row_col_to_pos(*self.highlight_pos)))
                        self.ch_pos = self.txt.pos_to_row_col(end)
                    else:
                        self.ch_pos = self.txt.pos_to_row_col(ch_pos + 1)
                if evt.mod & pygame.KMOD_SHIFT == 0:
                    self.highlight_pos = list(self.ch_pos)
            elif evt.key == pygame.K_UP:
                if self.ch_pos[1] > 0:
                    self.ch_pos[1] -= 1
                if self.cursor_col is not None:
                    self.ch_pos[0] = self.cursor_col
                else:
                    self.cursor_col = self.ch_pos[0]
                if self.ch_pos[0] > self.txt.get_draw_row_len(self.ch_pos[1]):
                    self.ch_pos[0] = self.txt.get_draw_row_len(self.ch_pos[1])
                if evt.mod & pygame.KMOD_SHIFT == 0:
                    self.highlight_pos = list(self.ch_pos)
                col_chg = False
            elif evt.key == pygame.K_DOWN:
                if self.ch_pos[1] + 1 < len(self.txt.lines):
                    self.ch_pos[1] += 1
                if self.cursor_col is not None:
                    self.ch_pos[0] = self.cursor_col
                else:
                    self.cursor_col = self.ch_pos[0]
                if self.ch_pos[0] > self.txt.get_draw_row_len(self.ch_pos[1]):
                    self.ch_pos[0] = self.txt.get_draw_row_len(self.ch_pos[1])
                if evt.mod & pygame.KMOD_SHIFT == 0:
                    self.highlight_pos = list(self.ch_pos)
                col_chg = False
            elif evt.mod & pygame.KMOD_CTRL > 0:
                start, end = sorted((ch_pos, self.txt.row_col_to_pos(*self.highlight_pos)))
                if evt.key == pygame.K_v:
                    data = None
                    for Item in clipboard_types:
                        data = self.clipboard.get(Item)
                        if data is not None:
                            break
                    if data is None or not self.on_pre_chg(evt):
                        return False
                    self.txt.replace(data, start, end)
                    self.ch_pos = self.txt.pos_to_row_col(start + len(data))
                    self.highlight_pos = list(self.ch_pos)
                    is_chg = True
                elif evt.key == pygame.K_c:
                    self.clipboard.put(pygame.SCRAP_TEXT, self.txt.get_str(start, end))
                elif evt.key == pygame.K_x:
                    if start == end or not self.on_pre_chg(evt):
                        return False
                    self.clipboard.put(pygame.SCRAP_TEXT, self.txt.get_str(start, end))
                    self.txt.delete(start, end)
                    self.ch_pos = self.txt.pos_to_row_col(start)
                    self.highlight_pos = self.txt.pos_to_row_col(start)
                    is_chg = True
            elif len(evt.unicode) > 0:
                if not self.on_pre_chg(evt):
                    return False
                start, end = sorted((ch_pos, self.txt.row_col_to_pos(*self.highlight_pos)))
                self.txt.replace(evt.unicode, start, end)
                self.ch_pos = self.txt.pos_to_row_col(start + 1)
                self.highlight_pos = list(self.ch_pos)
                is_chg = True
            if col_chg:
                self.cursor_col = None
            if is_chg and self.post_chg is not None:
                self.post_chg(self, evt)
            return True
        elif evt.type == EntryBox.cursor_timer_event_id:
            if self.is_selected:
                self.cursor_state = not self.cursor_state
                return True
        return False

    def draw(self, app):
        start, end = map(self.txt.pos_to_row_col,
                         sorted(map(self.txt.t_row_col_to_pos, [self.ch_pos, self.highlight_pos])))
        rtn = [None] * len(self.txt.lines)
        if len(self.colors) > 1:
            rtn.append(app.surf.fill(self.colors[1], self.coll_rect))
        for c in range(0, start[1]):
            draw_txt = self.txt.get_draw_row(c)
            if self.censor is not None:
                draw_txt = self.censor(draw_txt)
            img = self.fnt.render(draw_txt, True, self.colors[0])
            rtn[c] = app.surf.blit(img, (self.pos[0], self.pos[1] + self.line_h * c))
        if start == end:
            c = start[1]
            draw_txt = self.txt.get_draw_row(c)
            if self.censor is not None:
                draw_txt = self.censor(draw_txt)
            img = self.fnt.render(draw_txt, True, self.colors[0])
            rtn[c] = app.surf.blit(img, (self.pos[0], self.pos[1] + self.line_h * c))
        elif start[1] == end[1]:
            c = start[1]
            draw_txt = self.txt.get_draw_row(c)
            if self.censor is not None:
                draw_txt = self.censor(draw_txt)
            begin_w = get_pos_in_kern(self.fnt, draw_txt, start[0])
            end_w = get_pos_in_kern(self.fnt, draw_txt, end[0])
            img = pygame.Surface(self.fnt.size(draw_txt), pygame.SRCALPHA)
            img.blit(self.fnt.render(draw_txt[:start[0]], True, self.colors[0]), (0, 0))
            img.blit(self.fnt.render(draw_txt[start[0]:end[0]], True, *self.highlight_colors), (begin_w, 0))
            img.blit(self.fnt.render(draw_txt[end[0]:], True, self.colors[0]), (end_w, 0))
            rtn[c] = app.surf.blit(img, (self.pos[0], self.pos[1] + self.line_h * c))
        else:
            c = start[1]
            draw_txt = self.txt.get_draw_row(c)
            if self.censor is not None:
                draw_txt = self.censor(draw_txt)
            begin_w = get_pos_in_kern(self.fnt, draw_txt, start[0])
            img = pygame.Surface(self.fnt.size(draw_txt), pygame.SRCALPHA)
            img.blit(self.fnt.render(draw_txt[:start[0]], True, self.colors[0]), (0, 0))
            img.blit(self.fnt.render(draw_txt[start[0]:], True, *self.highlight_colors), (begin_w, 0))
            rtn[c] = app.surf.blit(img, (self.pos[0], self.pos[1] + self.line_h * c))
            c = end[1]
            draw_txt = self.txt.get_draw_row(c)
            if self.censor is not None:
                draw_txt = self.censor(draw_txt)
            end_w = get_pos_in_kern(self.fnt, draw_txt, end[0])
            img = pygame.Surface(self.fnt.size(draw_txt), pygame.SRCALPHA)
            img.blit(self.fnt.render(draw_txt[:end[0]], True, *self.highlight_colors), (0, 0))
            img.blit(self.fnt.render(draw_txt[end[0]:], True, self.colors[0]), (end_w, 0))
            rtn[c] = app.surf.blit(img, (self.pos[0], self.pos[1] + self.line_h * c))
        for c in range(start[1] + 1, end[1]):
            draw_txt = self.txt.get_draw_row(c)
            if self.censor is not None:
                draw_txt = self.censor(draw_txt)
            img = self.fnt.render(draw_txt, True, *self.highlight_colors)
            rtn[c] = app.surf.blit(img, (self.pos[0], self.pos[1] + self.line_h * c))
        for c in range(end[1] + 1, len(self.txt.lines)):
            draw_txt = self.txt.get_draw_row(c)
            if self.censor is not None:
                draw_txt = self.censor(draw_txt)
            img = self.fnt.render(draw_txt, True, self.colors[0])
            rtn[c] = app.surf.blit(img, (self.pos[0], self.pos[1] + self.line_h * c))
        if self.cursor_state:
            c = self.ch_pos[1]
            draw_txt = self.txt.get_draw_row(c)
            if self.censor is not None:
                draw_txt = self.censor(draw_txt)
            cursor_pos = (
                self.fnt.size(draw_txt[:self.ch_pos[0]])[0] + self.pos[0] - 1,
                self.pos[1] + self.line_h * self.ch_pos[1])
            rtn.append(app.surf.fill(self.colors[0], pygame.Rect(cursor_pos, (2, self.line_h))))
        self.prev_rect = rtn[-1].unionall(rtn[:-1])
        return [self.prev_rect]

    def pre_draw(self, app):
        if self.prev_rect is not None:
            if len(self.colors) >= 2:
                return [self.prev_rect]
            else:
                return [app.draw_background_rect(self.prev_rect)]
        return []

    def collide_pt(self, pt):
        return self.coll_rect.collidepoint(pt[0], pt[1])
