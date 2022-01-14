class Header:
    def __init__(self):
        self.header1_ = 0
        self.header2_ = 0
        self.header3_ = 0

    @property
    def header1(self):
        return self.header1_

    @property
    def header2(self):
        return self.header2_

    @property
    def header3(self):
        return self.header3_

    @property
    def header1next(self):
        self.header1_ += 1
        return self.header1_

    @property
    def header2next(self):
        self.header2_ += 1
        return self.header2_

    @property
    def header3next(self):
        self.header3_ += 1
        return self.header3_

    @property
    def header1reset(self):
        self.header1_ = 0
        return self.header1_

    @property
    def header2reset(self):
        self.header2_ = 0
        return self.header2_

    @property
    def header3reset(self):
        self.header3_ = 0
        return self.header3_
