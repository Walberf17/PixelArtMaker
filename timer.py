"""
Timer Class to create enemies
"""
# from definitions import create_enemies
from datetime import datetime as dt, timedelta
from functools import partial


class Timer:
    def __init__(self, time_var=5, recurrent=False, command=None, groups=None):
        self.initial_time = dt.now()
        self.timer = timedelta(seconds=time_var)
        self.recurrent = recurrent
        self.command = command
        if groups is None:
            groups = []
        if type(groups) not in [list, tuple, set]:
            groups = list(groups)
        for group in groups:
            if type(group) == list:
                group.append(self)
            elif type(group) == set:
                group.add(self)
        self.groups = groups

    def set_time_var(self, time_var=5):
        self.timer = timedelta(seconds=time_var)

    def update(self):
        now = dt.now()
        elapsed_time = now - self.initial_time
        if elapsed_time >= self.timer:
            if self.command:
                self.command()
            if self.recurrent:
                self.initial_time = dt.now()
            else:
                self.kill()
            return True

    def kill(self):
        for group in self.groups:
            if type(group) == list:
                group.remove(self)
            elif type(group) == set:
                group.discard_deck(self)
            group.remove(self)


if __name__ == '__main__':
    a = []

    b = Timer(time_var=1, recurrent=False, command=partial(print, 'teste'), groups=[a])
