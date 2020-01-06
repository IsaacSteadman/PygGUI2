from .misc import binary_approx1


class TextLineView(object):
    def __init__(self, string, line_sep="\n"):
        self.string = list()
        self.line_sep = "\n"
        self.lines = []
        self.set_str(string, line_sep)

    def set_str(self, string, line_sep=None):
        if line_sep is None:
            line_sep = self.line_sep
        else:
            self.line_sep = line_sep
        self.lines = [0] * (string.count(line_sep) + 1)
        pos = 0
        for c in range(1, len(self.lines)):
            pos = string.find(line_sep, pos) + len(line_sep)
            self.lines[c] = pos
        self.string = list(string)

    def get_row_len(self, row):
        if row >= len(self.lines):
            raise ValueError("row too big")
        return (self.lines[row + 1] if row + 1 < len(self.lines) else len(self.string)) - self.lines[row]

    def get_draw_row_len(self, row):
        if row >= len(self.lines):
            raise ValueError("row too big")
        return (
            self.lines[row + 1] - len(self.line_sep)
            if row + 1 < len(self.lines) else
            len(self.string)
        ) - self.lines[row]

    def row_col_to_pos(self, col, row):
        if col > self.get_row_len(row):
            raise ValueError("column too big for row %u of length %u" % (row, self.get_row_len(row)))
        return self.lines[row] + col

    def t_row_col_to_pos(self, col_row):
        col, row = col_row
        if col > self.get_row_len(row):
            raise ValueError("column too big for row %u of length %u" % (row, self.get_row_len(row)))
        return self.lines[row] + col

    def pos_to_row_col(self, pos):
        if pos > len(self.string):
            raise ValueError("pos out of range of string")
        row = binary_approx1(self.lines, pos)
        if row >= len(self.lines) and row > 0: row = len(self.lines) - 1
        col = pos - self.lines[row]
        return [col, row]

    def get_draw_row(self, row):
        end = (self.lines[row + 1] - len(self.line_sep)) if row + 1 < len(self.lines) else len(self.string)
        return u"".join(self.string[self.lines[row]:end]).replace("\0", "\x1b")

    def insert(self, string, pos):
        if string.count(self.line_sep) == 0:
            col, row = self.pos_to_row_col(pos)
            self.string[pos:pos] = string
            for c in range(row + 1, len(self.lines)):
                self.lines[c] += len(string)
        else:
            self.string[pos:pos] = string
            col, row = self.pos_to_row_col(pos)
            lines = [0] * (string.count(self.line_sep))
            prev_pos = 0
            for c in range(len(lines)):
                prev_pos = string.find(self.line_sep, prev_pos)
                lines[c] = prev_pos + pos
                prev_pos += len(self.line_sep)
            for c in range(row + 1, len(self.lines)):
                self.lines[c] += len(string)
            self.lines[row + 1:row + 1] = lines
            # self.set_str(self.string[:pos] + string + self.string[pos:])

    def replace(self, string, pos0, pos1):
        self.set_str(u"".join(self.string[:pos0]) + string + u"".join(self.string[pos1:]))

    def delete(self, pos0, pos1):
        self.set_str(u"".join(self.string[:pos0]) + u"".join(self.string[pos1:]))

    def get_str(self, pos0, pos1):
        return u"".join(self.string[pos0:pos1])


if __name__ == "__main__":
    def test():
        lst = [0, 12, 23, 33]
        for c in range(lst[-1] + 12):
            res = binary_approx1(lst, c)
            assert lst[res] <= c
            if res + 1 < len(lst):
                assert c < lst[res + 1]
        inst = TextLineView("hello\nhi\n\nnever")
        assert inst.lines == [0, 6, 9, 10]
        print(list(map(inst.pos_to_row_col, range(len(inst.string)))))
        inst.insert("hi", 9)
        print(inst.lines, repr(inst.string))
        assert inst.lines == [0, 6, 9, 12]
        print(inst.string)
        inst.insert("\nhehi", inst.row_col_to_pos(2, 2))
        print(inst.string)
        assert inst.lines == [0, 6, 9, 12, 17]
    test()
