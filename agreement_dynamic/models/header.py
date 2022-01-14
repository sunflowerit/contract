class Header:
    def __init__(self):
        self.value = 0

    def __call__(self):
        return self.value

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
