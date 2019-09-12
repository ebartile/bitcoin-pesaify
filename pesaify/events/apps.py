# -*- coding: utf-8 -*-
import sys
from django.apps import AppConfig
from django.db.models import signals

def connect_events_signals():
    from . import signal_handlers as handlers
    signals.post_save.connect(handlers.on_save_any_model, dispatch_uid="events_change")
    signals.post_delete.connect(handlers.on_delete_any_model, dispatch_uid="events_delete")


def disconnect_events_signals():
    signals.post_save.disconnect(dispatch_uid="events_change")
    signals.post_delete.disconnect(dispatch_uid="events_delete")


class EventsAppConfig(AppConfig):
    name = "pesaify.events"
    verbose_name = "Events App Config"

    def ready(self):
        connect_events_signals()
