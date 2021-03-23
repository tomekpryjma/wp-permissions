class Verbose:
    def __init__(self, verbose_on):
        self.verbose_on = verbose_on

    def print(self, msg):
        if self.verbose_on:
            print(msg)