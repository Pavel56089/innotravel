# -*- coding: utf-8 -*-


# python imports
from time import time


__all__ = ["StatefulObject"]


class StatefulObject(object):

    IDLE      = 0
    PENDING   = 1
    PAUSED    = 2
    RUNNING   = 3
    SUCCEEDED = 4
    FAILED    = 5
    STATUSES  = {
        "IDLE"     : IDLE,
        "PENDING"  : PENDING,
        "PAUSED"   : PAUSED,
        "RUNNING"  : RUNNING,
        "SUCCEEDED": SUCCEEDED,
        "FAILED"   : FAILED
    }
    MAX_LEN = len(max(STATUSES.keys(), key=lambda k: len(k)))

    COMP_OPS = ["==", "!=", "<", "<=", ">", ">="]

    def __init__(self, **kwargs):
        super(StatefulObject, self).__init__()

        self._status = self.IDLE

        self._started = None
        self._ended   = None

    @classmethod
    def status_int(cls, status):
        if isinstance(status, (int, float)):
            status = int(status)
            if status not in cls.STATUSES.values():
                raise ValueError("invalid status")
            return status
        else:
            status = str(status).upper()
            if status not in cls.STATUSES:
                raise ValueError("invalid status")
            return cls.STATUSES[status]

    @classmethod
    def status_str(cls, status):
        status = cls.status_int(status)
        for s, i in cls.STATUSES.items():
            if status == i:
                return s

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, status):
        old_status   = self.status
        self._status = self.status_int(status)

        if old_status != self.status:
            old_s   = self.status_str(old_status).center(self.MAX_LEN)
            new_s   = self.status_str(self.status).center(self.MAX_LEN)
            log_tpl = (old_s, new_s, repr(self))
            logger.debug("change status from %s to %s for %s" % log_tpl)

            if self.status == self.RUNNING:
                if self.started is None:
                    self._started = time()
            elif self.status > self.RUNNING:
                if self.ended is None:
                    self._ended = time()

    @property
    def started(self):
        return self._started

    @property
    def ended(self):
        return self._ended

    @property
    def runtime(self):
        if self.started is None:
            return None
        if self.ended is None:
            return time() - self.started
        return self.ended - self.started

    def _compare_status(self, op, status):
        if op not in self.COMP_OPS:
            raise ValueError("invalid operator")

        status = self.status_int(status)

        return eval("%s %s %s" % (self.status, op, status))

    def status_eq(self, status):
        return self._compare_status("==", status)

    def status_ne(self, status):
        return self._compare_status("!=", status)

    def status_lt(self, status):
        return self._compare_status("<", status)

    def status_le(self, status):
        return self._compare_status("<=", status)

    def status_gt(self, status):
        return self._compare_status(">", status)

    def status_ge(self, status):
        return self._compare_status(">=", status)


# trailing internal imports
from flow.utils import logger
