class Header:
    def __init__(self):
        self.value = 0

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
        return self.value
