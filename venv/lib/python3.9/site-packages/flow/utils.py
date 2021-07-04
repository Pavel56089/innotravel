# -*- coding: utf-8 -*-


# python imports
import sys
import logging
from uuid import uuid4


__all__ = []


class ColorFormatter(logging.Formatter):

    COLORS = {
        "NOTSET"  : "\033[3;37m", # white
        "DEBUG"   : "\033[3;32m", # green
        "INFO"    : "\033[3;36m", # cyan
        "WARNING" : "\033[3;33m", # yellow
        "ERROR"   : "\033[3;31m", # red
        "CRITICAL": "\033[41m"    # red background
    }

    END = "\033[0m"

    MAX_LEN = len(max(COLORS.keys(), key=lambda k: len(k)))

    def format(self, record):
        # colorize the level name and add an offset for pretty printing
        color  = self.COLORS.get(record.levelname, self.COLORS["NOTSET"])
        color = color.center(self.MAX_LEN)
        record.levelname = color + record.levelname + self.END

        # call super format
        return super(ColorFormatter, self).format(record)


fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
color_formatter = ColorFormatter(fmt=fmt)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(color_formatter)

logger = logging.getLogger("Flow")
logger.addHandler(console_handler)
logger.setLevel(logging.DEBUG)


def uuid(n=10):
    return uuid4().hex[:n]
