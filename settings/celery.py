# -*- coding: utf-8 -*-

import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')

from django.conf import settings

from . import celery_settings

app = Celery('pesaify')
app.config_from_object(celery_settings)
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
