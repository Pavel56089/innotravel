# -*- coding: utf-8 -*-


__all__ = ["NamedObject"]


class NamedObject(object):

    def __init__(self, **kwargs):
        name = kwargs.pop("name", None)

        object.__init__(self)

        self._name = uuid()
        if name is not None:
            self.name = name

    def __repr__(self):
        tpl = (self.__class__.__name__, self.name, hex(id(self)))
        return "<%s '%s' at %s>" % tpl

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        if name is None:
            raise TypeError("invalid name")
        self._name = str(name)


# trailing internal imports
from flow.utils import logger, uuid
