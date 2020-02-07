from collections import UserDict
from datetime import datetime
from datetime import timedelta


class CacheDict(UserDict):

    times = {}

    def __init__(self, dict={}, keytime=60, **kwargs):
        super().__init__(dict, **kwargs)

        self.keytime = keytime

    def __getitem__(self, key):

        if not self.times.get(key):
            raise KeyError(key)

        elapsed_time = datetime.now() - self.times.get(key)
        if elapsed_time.seconds <= 60:
            return super().__getitem__(key)
        else:
            self.data.pop(key)
            raise KeyError(key)

    def __setitem__(self, key, item):
        self.times[key] = datetime.now()

        return super().__setitem__(key, item)
