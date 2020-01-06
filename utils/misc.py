from typing import Union


class FuncListView(object):
    def __init__(self, func, length):
        self.cache = [None] * length
        self.func = func

    def __len__(self):
        return len(self.cache)

    def __getitem__(self, index):
        if self.cache[index] is None:
            self.cache[index] = self.func(index)
        return self.cache[index]


def binary_approx1(lst: Union[list, FuncListView], v) -> int:
    length = len(lst)
    cur_len = length
    pos = length >> 1
    while cur_len > 0:
        if (pos + 1 >= len(lst) or v < lst[pos + 1]) and v >= lst[pos]:
            return pos
        elif v < lst[pos]:
            cur_len >>= 1
            pos -= (cur_len + 1) >> 1
        else:
            cur_len = (cur_len - 1) >> 1
            pos += (cur_len >> 1) + 1
    return length


def binary_approx(lst: Union[list, FuncListView], v) -> int:
    length = len(lst)
    cur_len = length
    pos = length >> 1
    while cur_len > 0:
        if v <= lst[pos] and (pos == 0 or v >= lst[pos - 1]):
            return pos
        elif v < lst[pos]:
            cur_len >>= 1
            pos -= (cur_len + 1) >> 1
        else:
            cur_len = (cur_len - 1) >> 1
            pos += (cur_len >> 1) + 1
    return length