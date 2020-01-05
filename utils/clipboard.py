import pygame


class ClipboardHandler(object):
    def put(self, typ, data):
        pass

    def get(self, typ):
        pass


class PygClipboard(ClipboardHandler):
    def __init__(self):
        pygame.scrap.init()

    def put(self, typ, data):
        attrs = {"charset": "utf-16-le"}
        for attr in typ.split(";")[1:]:
            a = attr.split('=')
            if len(a) != 2:
                continue
            a, b = a
            attrs[a] = b
        pygame.scrap.put(typ, data.encode(attrs["charset"]))

    def get(self, typ):
        attrs = {"charset": "utf-16-le"}
        for attr in typ.split(";")[1:]:
            a = attr.split('=')
            if len(a) != 2: continue
            a, b = a
            attrs[a] = b
        return pygame.scrap.get(typ).decode(attrs["charset"])


class PyperClipboard(ClipboardHandler):
    pyperclip = None

    def __init__(self):
        if self.pyperclip is None:
            import pyperclip
            self.pyperclip = pyperclip
            PyperClipboard.pyperclip = pyperclip

    def put(self, typ, data):
        assert typ == "UTF8_STRING" or typ.startswith("text/plain"), "PyperClipboard only works with text"
        self.pyperclip.copy(data)

    def get(self, typ):
        assert typ == "UTF8_STRING" or typ.startswith("text/plain"), "PyperClipboard only works with text"
        return self.pyperclip.paste()
