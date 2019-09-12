# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function
import sys

__title__ = 'Pesaify'
__version__ = '1.0.0'
__author__ = 'Pesaify Inc'
__license__ = ''
__copyright__ = 'Copyright 2019 Pesaify Inc'
VERSION = (1, 0, 0, 'beta', 0)

def get_version(*args, **kwargs):
    # Don't litter django/__init__.py with all the get_version stuff.
    # Only import if it's actually called.
    from .get_version import get_version
    return get_version(*args, **kwargs)

# check python version
if sys.version[:5] < '3':
    sys.exit('Your host needs to use PYTHON 3 or higher to run this version of Pesaify!')

from .celery_settings import *

try:
    from .local import *
except ImportError:
    from .development import *
