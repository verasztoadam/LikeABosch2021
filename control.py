from simulation import*

HARD_STOP_DIST = 1

class Control:
    def __init__(self, move=False):
        self.output = move
        self.input = []
        for i in range(18):
            self.input[i] = 0

    def min_value(self):
        min_val = 1000
        for i in self.input:
            if self.input[i] < min_val:
                min_val = self.input[i]
        return min_val

    def step(self):
        if self.min_value() < HARD_STOP_DIST:
            self.output = 0
        else:
            self.output = 1
