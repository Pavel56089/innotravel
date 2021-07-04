# -*- coding: utf-8 -*-


# python imports
from time import sleep
from threading import Thread

# leading internal imports
from flow.name import NamedObject
from flow.status import StatefulObject
from flow.observer import Observer


__all__ = ["AbstractWorkload", "Workload", "Workflow"]


class AbstractWorkload(NamedObject, StatefulObject, Observer):

    def __init__(self, **kwargs):
        priority  = kwargs.pop("priority", None)
        scheduler = kwargs.pop("scheduler", None)

        NamedObject.__init__(self, **kwargs)
        StatefulObject.__init__(self, **kwargs)
        Observer.__init__(self, **kwargs)

        self._priority = 0
        if priority is not None:
            self.priority = priority

        self._scheduler = None
        if scheduler is not None:
            self.scheduler = scheduler

        self._output = None
        self._error  = None

        self._workflow          = None
        self._initial           = False
        self._dependency        = None
        self._combined_priority = None

    @property
    def priority(self):
        return self._priority

    @priority.setter
    def priority(self, priority):
        if not isinstance(priority, int):
            raise TypeError("invalid priority")

        self._priority = priority

    @property
    def scheduler(self):
        return self._scheduler

    @scheduler.setter
    def scheduler(self, scheduler):
        if not isinstance(scheduler, Scheduler):
            raise TypeError("invalid scheduler")

        self._scheduler = scheduler

    @property
    def output(self):
        return self._output

    @property
    def error(self):
        return self._error

    @property
    def workflow(self):
        return self._workflow

    @workflow.setter
    def workflow(self, workflow):
        if not isinstance(workflow, Workflow) and workflow is not None:
            raise TypeError("invalid workflow")

        # if there is already a set workflow
        # remove self from its workloads
        if self.workflow is not None and self in self.workflow:
            self.workflow.remove_workload(self)

        self._workflow = workflow

        # add self to workflow's workloads
        if workflow is not None and self not in workflow:
            workflow.add_workload(self)

    @property
    def initial(self):
        return self._initial

    @initial.setter
    def initial(self, initial):
        if not isinstance(initial, bool):
            raise TypeError("invalid initial")

        self._initial = initial

    @property
    def dependency(self):
        return self._dependency

    @property
    def combined_priority(self):
        return self._combined_priority

    def find_combined_priority(self):
        combined_priority = self.priority

        if not self.initial:
            workflow = self._workflow
            while workflow is not None:
                combined_priority += workflow.priority
                if workflow.initial:
                    break
                workflow = workflow.workflow

        self._combined_priority = combined_priority
        return combined_priority

    def find_scheduler(self):
        if self.scheduler is not None:
            return self.scheduler
        elif self.workflow:
            return self.workflow.find_scheduler()
        else:
            return None

    def find_dependency(self):
        if self.initial:
            dep = None

        elif self.workflow is None:
            dep = None

        elif self.workflow.mode == self.workflow.PARALLEL:
            dep = self.workflow.find_dependency()

        elif self.workflow.mode == self.workflow.SEQUENTIAL:
            index = self.workflow.index(self)
            if index == 0:
                dep = self.workflow.find_dependency()
            else:
                dep = self.workflow[index - 1]

        self._dependency = dep
        return dep

    def start(self, initial=True):
        raise NotImplementedError

    def run(self):
        raise NotImplementedError

    def suspend(self):
        raise NotImplementedError

    def resume(self):
        raise NotImplementedError

    def terminate(self):
        raise NotImplementedError

    def kill(self):
        raise NotImplementedError


class Workload(AbstractWorkload):

    @StatefulObject.status.setter
    def status(self, status):
        old_status = self.status

        StatefulObject.status.fset(self, status)

        # tell the workflow when the status changed
        if old_status != self.status and self.workflow is not None:
            self.workflow._on_workload_status(self, self.status)

    def start(self, initial=True):
        scheduler = self.find_scheduler()
        if scheduler is None:
            raise RuntimeError("unknown scheduler")

        self.initial = initial

        self.find_dependency()
        self.find_combined_priority()

        self.status = self.PENDING

        # add ourself to the scheduler
        scheduler.add_workload(self)

        # if initial, start the scheduler
        if initial:
            scheduler.start()


class Workflow(AbstractWorkload):

    SEQUENTIAL = "sequential"
    PARALLEL   = "parallel"
    MODES      = [SEQUENTIAL, PARALLEL]

    def __init__(self, **kwargs):
        mode = kwargs.pop("mode", None)

        AbstractWorkload.__init__(self, **kwargs)

        self._mode = self.SEQUENTIAL
        if mode is not None:
            self.mode = mode

        self._workloads = []

    def __len__(self, *args, **kwargs):
        return self._workloads.__len__(*args, **kwargs)

    def __contains__(self, *args, **kwargs):
        return self._workloads.__contains__(*args, **kwargs)

    def __iter__(self, *args, **kwargs):
        return self._workloads.__iter__(*args, **kwargs)

    def __getitem__(self, *args, **kwargs):
        return self._workloads.__getitem__(*args, **kwargs)

    @property
    def mode(self):
        return self._mode

    @mode.setter
    def mode(self, mode):
        if mode not in self.MODES:
            raise ValueError("invalid mode")
        self._mode = mode

    def has_workload(self, workload, recursive=False):
        if workload in self or not recursive:
            return workload in self
        else:
            for wf in self:
                if not isinstance(wf, Workflow):
                    continue
                if wf.has_workload(workload, recursive=recursive):
                    return True
            return False

    def add_workload(self, workload, index=None):
        if not isinstance(workload, AbstractWorkload):
            raise TypeError("invalid workload")

        if workload in self:
            self.remove_workload(workload)

        if index is None:
            self._workloads.append(workload)
        else:
            self._workloads.insert(index, workload)

        # set workfload's workflow to self
        if workload.workflow != self:
            workload.workflow = self

    def remove_workload(self, workload):
        if workload in self:
            self._workloads.remove(workload)

        if workload.workflow == self:
            workload.workflow = None

    def index(self, workload):
        if workload not in self:
            return -1
        return self._workloads.index(workload)

    def start(self, initial=True):
        scheduler = self.find_scheduler()
        if scheduler is None:
            raise RuntimeError("unknown scheduler")

        self.initial = initial

        self.find_dependency()
        self.find_combined_priority()

        self.status = self.PENDING

        # we're done when there's no workload
        if len(self) == 0:
            self.status = self.SUCCEEDED
            return

        # start all workload's
        for wl in self:
            wl.start(initial=False)

        # if initial, start all distinct schedulers
        if initial:
            schedulers = [scheduler]
            lookup = [w for w in self]
            while len(lookup):
                w = lookup.pop(0)
                s = w.scheduler
                if s is not None and s not in schedulers:
                    schedulers.append(s)
                if isinstance(w, Workflow):
                    lookup.extend([w2 for w2 in w])
            for s in schedulers:
                s.start()

    def _on_workload_status(self, workload, status):
        if self.status == self.PENDING:
            if workload.status == workload.RUNNING:
                self.status = self.RUNNING

        elif self.status == self.RUNNING:
            finished    = True
            n_succeeded = 0
            n_failed    = 0
            for w in self:
                if w.status == w.SUCCEEDED:
                    n_succeeded += 1
                elif w.status == w.FAILED:
                    n_failed += 1
                else:
                    finished = False
                    break

            if not finished:
                return

            if self.mode == self.PARALLEL:
                self.status = self.SUCCEEDED if n_succeeded > 0 else self.FAILED
            elif self.mode == self.SEQUENTIAL:
                self.status = self.FAILED if n_failed > 0 else self.SUCCEEDED


# trailing internal imports
from flow.scheduler import Scheduler
from flow.utils import logger, uuid
