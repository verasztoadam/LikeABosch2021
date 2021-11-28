HARD_STOP_DIST = 1


class Control:
    def __init__(self):
        self.output = 1
        self.input = []

    def min_value(self):
        """Min search"""
        min_val = 1000
        for i in self.input:
            if i < min_val and i != 0:
                min_val = i
        return min_val

    def get_speed(self):
        if self.min_value() < HARD_STOP_DIST:
            self.output = 0
        else:
            self.output = 1
        return self.output