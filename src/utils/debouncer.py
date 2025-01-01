from threading import Timer
from typing import Callable
from functools import wraps

class Debouncer:
    """防抖动处理类"""
    def __init__(self, delay: float):
        self.delay = delay
        self.timer = None

    def __call__(self, func: Callable):
        @wraps(func)
        def wrapped(*args, **kwargs):
            def call_func():
                func(*args, **kwargs)

            if self.timer:
                self.timer.cancel()

            self.timer = Timer(self.delay, call_func)
            self.timer.start()

        return wrapped 