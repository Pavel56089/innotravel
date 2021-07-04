# -*- coding: utf-8 -*-


# python imports
from time import time, sleep
from threading import Thread

# leading internal imports
from flow.name import NamedObject
from flow.status import StatefulObject
from flow.observer import Observer


__all__ = ["Scheduler"]


class Scheduler(NamedObject, StatefulObject, Observer):

    def __init__(self, **kwargs):
        nprocs = kwargs.get("nprocs", None)

        NamedObject.__init__(self, **kwargs)
        StatefulObject.__init__(self, **kwargs)
        Observer.__init__(self, **kwargs)

        self._nprocs = 1
        if nprocs is not None:
            self.nprocs = nprocs

        self._pending  = []
        self._running  = []
        self._finished = []

    def __len__(self):
        return len(self._pending) + len(self._running) + len(self._finished)

    def __contains__(self, workload):
        return workload in self._pending

    @property
    def nprocs(self):
        return self._nprocs

    @nprocs.setter
    def nprocs(self, nprocs):
        if not isinstance(nprocs, int):
            raise TypeError("invalid nprocs")
        if nprocs <= 0:
            raise ValueError("invalid nprocs")

        self._nprocs = nprocs

    def add_workload(self, workload):
        if not isinstance(workload, Workload):
            raise TypeError("invalid workload")

        if self.status != self.IDLE:
            return

        if workload.status != workload.PENDING:
            return

        if workload in self:
            return

        self._pending.append(workload)

    def start(self):
        if self.status != self.IDLE:
            return

        self.status = self.RUNNING

        # sort the pending queue by the workload's combined priority
        self._pending.sort(key=lambda w: -w.combined_priority)

        self.start_observing()

    def observe(self):
        # remove finished workloads from running queue
        for w in self._running:
            if w.status == w.SUCCEEDED or w.status == w.FAILED:
                self._running.remove(w)
                self._finished.append(w)

        # try to start new workloads
        max_add = self.nprocs - len(self._running)
        add     = []
        for w in self._pending:
            if len(add) == max_add:
                break

            dep = w.dependency

            if dep is None or dep.status == dep.SUCCEEDED:
                add.append(w)
            elif dep is not None and dep.status == dep.FAILED:
                self._pending.remove(w)
                self._finished.append(w)
                w._error = "failed due to failed dependency"
                w.status == w.FAILED

        for w in add:
            self._pending.remove(w)
            self._running.append(w)
            w.run()

        # check if we're done
        if len(self._finished) == len(self):
            self.status = self.SUCCEEDED
            self.stop_observing()


# trailing internal imports
from flow.workload import Workload
from flow.utils import logger
