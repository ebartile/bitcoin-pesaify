# -*- coding: utf-8 -*-
import collections

from django.db import connection
from django.utils.translation import ugettext_lazy as _

from pesaify.base.utils import json
from pesaify.base.utils.db import get_typename_for_model_instance
from . import middleware as mw
from . import backends


# The complete list of content types
# of allowed models for change events
watched_types = set([
    # TODO add watched type models
    "users.user",
    "users.business",
    "users.mobilemoneysettlement",
    "users.cryptosettlement",
    "users.banksettlement",
])


def emit_event(data:dict, routing_key:str, *,
               sessionid:str=None, channel:str="events",
               on_commit:bool=True):
    if not sessionid:
        sessionid = mw.get_current_session_id()

    data = {"session_id": sessionid,
            "data": data}

    backend = backends.get_events_backend()

    def backend_emit_event():
        backend.emit_event(message=json.dumps(data), routing_key=routing_key, channel=channel)

    if on_commit:
        connection.on_commit(backend_emit_event)
    else:
        backend_emit_event()


def emit_event_for_model(obj, *, type:str="change", channel:str="events",
                         content_type:str=None, sessionid:str=None):
    """
    Sends a model change event.
    """
    assert type in set(["create", "change", "delete"])

    if not content_type:
        content_type = get_typename_for_model_instance(obj)

    pk = getattr(obj, "pk", None)

    app_name, model_name = content_type.split(".", 1)
    routing_key = "changes.{0}.{1}.{2}".format(model_name, pk, app_name)

    data = {"type": type,
            "matches": content_type,
            "pk": pk}

    return emit_event(routing_key=routing_key,
                      channel=channel,
                      sessionid=sessionid,
                      data=data)

