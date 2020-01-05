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
