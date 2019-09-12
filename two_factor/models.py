from __future__ import absolute_import, division, unicode_literals

import logging
from binascii import unhexlify

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django_otp.models import Device
from django_otp.oath import totp
from django_otp.util import hex_validator, random_hex
logger = logging.getLogger(__name__)

def get_available_methods():
    methods = [('generator', _('Token generator'))]
    return methods


def key_validator(*args, **kwargs):
    """Wraps hex_validator generator, to keep makemigrations happy."""
    return hex_validator()(*args, **kwargs)

