# -*- coding: utf-8 -*-
from .common import *

DEBUG = True

TEMPLATES[0]["OPTIONS"]['context_processors'] += "django.template.context_processors.debug"

INSTALLED_APPS = INSTALLED_APPS + [
    'django_extensions',
]

with open('private_key_dev.pem', mode='rb') as private_file:
    PRIVKEY = private_file.read()
