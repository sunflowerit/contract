class Header:
    def __init__(self, child=False, parent=False):
        self.value = 0
        self.child = child
        if parent:
            parent.child = self

    @property
    def next(self):
        self.value += 1
        return self.value

    @property
    def previous(self):
        if self.value:
            self.value -= 1
        return self.value

    @property
    def reset(self):
        self.value = 0
        self.child.reset
        return self.value
