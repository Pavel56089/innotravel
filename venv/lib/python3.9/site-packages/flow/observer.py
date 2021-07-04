# -*- coding: utf-8 -*-


# python imports
from time import sleep
from threading import Thread


__all__ = ["Observer"]


class Observer(object):

    def __init__(self, **kwargs):
        interval = kwargs.pop("interval", None)

        object.__init__(self)

        self._interval = 3
        self._interval_set = False
        if interval is not None:
            self.interval = interval

        self._thread    = None
        self._stop_flag = False

    @property
    def interval(self):
        return self._interval

    @interval.setter
    def interval(self, interval):
        if not isinstance(interval, (int, float)):
            raise TypeError("invalid interval")
        if interval <= 0:
            raise ValueError("invalid interval")

        self._interval = interval
        self._interval_set = True

    def interval_is_set(self):
        return self._interval_set

    def is_observing(self):
        return self._thread is not None

    def join(self, timeout=None):
        if self.is_observing():
            self._thread.join(timeout)

    def start_observing(self, *args, **kwargs):
        if self.is_observing():
            return

        self._thread = Thread(target=self._observer_loop,
                              args=args, kwargs=kwargs)

        self._stop_flag = False
        self._thread.start()

    def stop_observing(self):
        self._stop_flag = True

    def _observer_loop(self, *args, **kwargs):
        while not self._stop_flag:
            self.observe(*args, **kwargs)
            sleep(self.interval)

        del self._thread
        self._thread  = None
        self._stop_flag = False

    def observe(self, *args, **kwargs):
        raise NotImplementedError
