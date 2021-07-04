#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
flow
"""


__author__     = "Marcel Rieger"
__copyright__  = "Copyright 2014, Marcel Rieger"
__credits__    = ["Marcel Rieger"]
__license__    = "MIT"
__maintainer__ = "Marcel Rieger"
__status__     = "Development"
__version__    = "0.0.1"


# python imports
import os
import sys


# adjust the path to simplyfy project interal imports
thisdir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, thisdir)


# provisioning imports
from flow.workload import Workload, Workflow
from flow.scheduler import Scheduler
from flow.utils import logger
