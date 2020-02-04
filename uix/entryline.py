from typing import Callable, Optional, List
from ..utils.clipboard import PyperClipboard
from ..utils.misc import FuncListView, binary_approx
from ..base.pyg_types import Color, Point
from .pyg_ctl import PygCtl
import pygame


antialias = True


sym_ch = "!@#$%^&*()[]{}:;<>,./?~`-+=\\|"


def get_pos_in_kern(fnt: pygame.font.FontType, txt0: str, pos: int) -> int:
    cur_w = fnt.size(txt0[:pos + 1])[0]
    ch_w = fnt.size(txt0[pos:pos + 1])[0]
    return cur_w - ch_w


clipboard_types = ["text/plain;charset=utf-8", "UTF8_STRING", pygame.SCRAP_TEXT]


class EntryLine(PygCtl):
    cursor_timer_event_id = pygame.USEREVENT + 1
    # cursor Threshold, the fraction of character width
    #  that represents border between 2 char positions
    cursor_thresh = .3
    cursor = ((16, 24), (8, 12)) + pygame.cursors.compile((
        "                ",
        "                ",
        "                ",
        "   XXXX XXXX    ",
        "       X        ",
        "       X        ",
        "       X        ",
        "       X        ",
        "       X        ",
        "       X        ",
        "       X        ",
        "       X        ",
        "       X        ",
        "       X        ",
        "       X        ",
        "       X        ",
        "       X        ",
        "       X        ",
        "       X        ",
        "       X        ",
        "   XXXX XXXX    ",
        "                ",
        "                ",
        "                "),
        black='.', white='O', xor='X')

    @staticmethod
    def next_word(lst_txt: List[str], txt_pos):
        cur_type = -1
        for c in range(txt_pos, len(lst_txt)):
            ch = lst_txt[c]
            if ch.isalnum() or ch == '_':
                if cur_type == -1:
                    cur_type = 0
                elif cur_type != 0:
                    return c
            elif ch in sym_ch:
                if cur_type == -1:
                    cur_type = 1
                elif cur_type != 1:
                    return c
            elif ch.isspace():
                if cur_type != -1:
                    return c
            else:
                if cur_type == -1:
                    cur_type = 2
                elif cur_type != 2:
                    return c
        return len(lst_txt)

    @staticmethod
    def prev_word(lst_txt, txt_pos):
        cur_type = -1
        for c in range(txt_pos, 0, -1):
            ch = lst_txt[c - 1]
            if ch.isalnum() or ch == '_':
                if cur_type == -1:
                    cur_type = 0
                elif cur_type != 0:
                    return c
            elif ch in sym_ch:
                if cur_type == -1:
                    cur_type = 1
                elif cur_type != 1:
                    return c
            elif ch.isspace():
                if cur_type != -1:
                    return c
            else:
                if cur_type == -1:
                    cur_type = 2
                elif cur_type != 2:
                    return c
        return 0

    @classmethod
    def init_timer(cls, evt_code=None):
        if evt_code is not None:
            cls.cursor_timer_event_id = evt_code
        pygame.time.set_timer(cls.cursor_timer_event_id, 500)
        cls.clipboard = PyperClipboard()

    def __init__(self, fnt: pygame.font.FontType, pos: Point, size: Point, colors: List[Color],
                 pre_chg: Optional[Callable[["EntryLine", pygame.event.EventType], bool]] = None,
                 post_chg: Optional[Callable[["EntryLine", pygame.event.EventType], None]] = None,
                 enter: Optional[Callable[["EntryLine"], None]] = None,
                 default_text: str = "",
                 censor: Optional[Callable[[str], str]] = None):
        super().__init__()
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
        self.highlight_pos: int = 0
        self.txt: List[str] = list(default_text)
        self.ch_pos: int = 0
        self.ch_off: int = 0  # x offset in pixels
        self.cur_key = None
        self.coll_rect: pygame.rect.RectType = pygame.rect.Rect(self.pos, self.size)
        self.prev_rect: pygame.rect.RectType = self.coll_rect
        self.fnt = fnt
        self.old_cursor: Optional[tuple] = None
        self.cursor_state = True
        self.aa = antialias

    def on_evt(self, app, evt, pos):
        if evt.type == pygame.MOUSEBUTTONDOWN:
            draw_txt = u"".join(self.txt)
            if self.censor is not None:
                draw_txt = self.censor(draw_txt)
            self.highlight = True
            self.is_selected = True
            pos = (pos[0] - self.pos[0], pos[1] - self.pos[1])
            cursor_thresh = EntryLine.cursor_thresh

            def get_size_text(x):
                return self.fnt.size(draw_txt[:x])[0]

            lst_v = FuncListView(get_size_text, len(draw_txt))
            # since lst_v[0] == 0 and pos[0] >= 0 is True, result->ch_pos >= 1
            ch_pos = binary_approx(lst_v, pos[0])
            if ch_pos < len(lst_v):
                off_x = lst_v[ch_pos - 1]
                ch_w = lst_v[ch_pos] - off_x
                if pos[0] - off_x <= cursor_thresh * ch_w:
                    ch_pos -= 1
            self.ch_pos = ch_pos
            self.highlight_pos = ch_pos
            return True
        return False

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

    def on_pre_chg(self, evt):
        return self.pre_chg is None or self.pre_chg(self, evt)

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
            draw_txt = u"".join(self.txt)
            if self.censor is not None:
                draw_txt = self.censor(draw_txt)
            pos = evt.pos
            pos = [pos[0] - self.pos[0], pos[1] - self.pos[1]]
            if pos[0] < 0:
                pos[0] = 0
            cursor_thresh = EntryLine.cursor_thresh

            def get_size_text(x):
                return self.fnt.size(draw_txt[:x])[0]

            lst_v = FuncListView(get_size_text, len(draw_txt))
            # since lst_v[0] == 0 and pos[0] >= 0 is True, result->ch_pos >= 1
            ch_pos = binary_approx(lst_v, pos[0])
            if ch_pos < len(lst_v):
                off_x = lst_v[ch_pos - 1]
                ch_w = lst_v[ch_pos] - off_x
                if pos[0] - off_x <= cursor_thresh * ch_w:
                    ch_pos -= 1
            self.ch_pos = ch_pos
            return True
        elif evt.type == pygame.KEYDOWN and self.is_selected:
            is_chg = False
            if evt.key == pygame.K_BACKSPACE:
                if not ((self.ch_pos > 0 or self.ch_pos != self.highlight_pos) and self.on_pre_chg(evt)):
                    return False
                elif evt.mod & pygame.KMOD_CTRL > 0:
                    start = EntryLine.prev_word(self.txt, self.ch_pos)
                    self.txt[start:self.ch_pos] = []
                    off = self.ch_pos - start
                    do_off = 0  # Default make highlight_pos = ch_pos
                    if self.highlight_pos > self.ch_pos:
                        do_off = 1  # Offset highlight_pos same amount as ch_pos
                    elif self.highlight_pos < self.ch_pos - start:
                        do_off = 2  # Leave highlight_pos Alone
                    self.ch_pos = start
                    if do_off == 1:
                        self.highlight_pos -= off
                    elif do_off == 0:
                        self.highlight_pos = self.ch_pos
                    is_chg = True
                else:
                    if self.ch_pos != self.highlight_pos:
                        start, end = sorted((self.ch_pos, self.highlight_pos))
                        self.txt[start:end] = []
                        self.ch_pos = start
                    else:
                        self.ch_pos -= 1
                        self.txt.pop(self.ch_pos)
                    is_chg = True
                    self.highlight_pos = self.ch_pos
            elif evt.key == pygame.K_DELETE:
                if not ((self.ch_pos < len(self.txt) or self.ch_pos != self.highlight_pos) and self.on_pre_chg(evt)):
                    return False
                elif evt.mod & pygame.KMOD_CTRL > 0:
                    end = EntryLine.next_word(self.txt, self.ch_pos)
                    self.txt[self.ch_pos:end] = []
                    off = end - self.ch_pos
                    if self.highlight_pos > self.ch_pos:
                        self.highlight_pos -= off
                    is_chg = True
                else:
                    if self.ch_pos != self.highlight_pos:
                        start, end = sorted((self.ch_pos, self.highlight_pos))
                        self.txt[start:end] = []
                        self.ch_pos = start
                        self.highlight_pos = start
                    else:
                        self.txt.pop(self.ch_pos)
                    is_chg = True
                    self.highlight_pos = self.ch_pos
            elif evt.key == pygame.K_HOME:
                self.ch_pos = 0
                if evt.mod & pygame.KMOD_SHIFT == 0:
                    self.highlight_pos = self.ch_pos
            elif evt.key == pygame.K_END:
                self.ch_pos = len(self.txt)
                if evt.mod & pygame.KMOD_SHIFT == 0:
                    self.highlight_pos = self.ch_pos
            elif evt.key == pygame.K_RETURN:
                if self.enter is not None:
                    self.enter(self)
            elif evt.key == pygame.K_LEFT:
                if evt.mod & pygame.KMOD_CTRL > 0:
                    self.ch_pos = EntryLine.prev_word(self.txt, self.ch_pos)
                elif self.ch_pos > 0:
                    if evt.mod & pygame.KMOD_SHIFT == 0 and self.ch_pos != self.highlight_pos:
                        start, end = sorted((self.ch_pos, self.highlight_pos))
                        self.ch_pos = start
                    else:
                        self.ch_pos -= 1
                if evt.mod & pygame.KMOD_SHIFT == 0:
                    self.highlight_pos = self.ch_pos
            elif evt.key == pygame.K_RIGHT:
                if evt.mod & pygame.KMOD_CTRL > 0:
                    self.ch_pos = EntryLine.next_word(self.txt, self.ch_pos)
                elif self.ch_pos < len(self.txt):
                    if evt.mod & pygame.KMOD_SHIFT == 0 and self.ch_pos != self.highlight_pos:
                        start, end = sorted((self.ch_pos, self.highlight_pos))
                        self.ch_pos = end
                    else:
                        self.ch_pos += 1
                if evt.mod & pygame.KMOD_SHIFT == 0:
                    self.highlight_pos = self.ch_pos
            elif evt.mod & pygame.KMOD_CTRL > 0:
                start, end = sorted((self.ch_pos, self.highlight_pos))
                if evt.key == pygame.K_v:
                    data = None
                    for Item in clipboard_types:
                        data = self.clipboard.get(Item)
                        if data is not None:
                            break
                    if data is None or not self.on_pre_chg(evt):
                        return False
                    self.txt[start:end] = data
                    self.ch_pos = start + len(data)
                    self.highlight_pos = self.ch_pos
                    is_chg = True
                elif evt.key == pygame.K_c:
                    self.clipboard.put(pygame.SCRAP_TEXT, u"".join(self.txt[start:end]))
                elif evt.key == pygame.K_x:
                    if start == end or not self.on_pre_chg(evt):
                        return False
                    self.clipboard.put(pygame.SCRAP_TEXT, u"".join(self.txt[start:end]))
                    self.txt[start:end] = []
                    self.ch_pos = start
                    self.highlight_pos = start
                    is_chg = True
            elif len(evt.unicode) > 0:
                if not self.on_pre_chg(evt):
                    return False
                start, end = sorted((self.ch_pos, self.highlight_pos))
                self.txt[start:end] = evt.unicode
                self.ch_pos = start + 1
                self.highlight_pos = self.ch_pos
                is_chg = True
            if is_chg and self.post_chg is not None:
                self.post_chg(self, evt)
            return True
        elif evt.type == EntryLine.cursor_timer_event_id:
            if self.is_selected:
                self.cursor_state = not self.cursor_state
                return True
        return False

    def draw(self, app):
        draw_txt = u"".join(self.txt)
        if self.censor is not None:
            draw_txt = self.censor(draw_txt)
        if self.ch_pos != self.highlight_pos:
            start, end = sorted((self.ch_pos, self.highlight_pos))
            begin_w = get_pos_in_kern(self.fnt, draw_txt, start)
            end_w = get_pos_in_kern(self.fnt, draw_txt, end)
            img = pygame.Surface(self.fnt.size(draw_txt), pygame.SRCALPHA)
            img.blit(self.fnt.render(draw_txt[:start], self.aa, self.colors[0]), (0, 0))
            img.blit(self.fnt.render(draw_txt[start:end], self.aa, *self.highlight_colors), (begin_w, 0))
            img.blit(self.fnt.render(draw_txt[end:], self.aa, self.colors[0]), (end_w, 0))
        else:
            img = self.fnt.render(draw_txt, self.aa, self.colors[0])
        rtn = []
        if len(self.colors) > 1:
            rtn.append(app.surf.fill(self.colors[1], self.coll_rect))
        rtn.append(app.surf.blit(img, self.pos))
        if self.cursor_state:
            cursor_x = self.fnt.size(draw_txt[:self.ch_pos])[0] + self.pos[0] - 1
            rtn.append(app.surf.fill(self.colors[0], pygame.Rect(cursor_x, self.pos[1], 2, img.get_height())))
        self.prev_rect = rtn[-1].unionall(rtn[:-1])
        return rtn

    def pre_draw(self, app):
        if self.prev_rect is not None:
            if len(self.colors) >= 2:
                return [self.prev_rect]
            else:
                return [app.draw_background_rect(self.prev_rect)]
        return []

    def collide_pt(self, pt):
        return self.coll_rect.collidepoint(pt[0], pt[1])
