# -*- coding: utf-8 -*-
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import _get_queryset

def get_object_or_none(klass, *args, **kwargs):
    """
    Uses get() to return an object, or None if the object does not exist.

    klass may be a Model, Manager, or QuerySet object. All other passed
    arguments and keyword arguments are used in the get() query.

    Note: Like with get(), an MultipleObjectsReturned will be raised if more
    than one object is found.
    """
    queryset = _get_queryset(klass)
    try:
        return queryset.get(*args, **kwargs)
    except queryset.model.DoesNotExist:
        return None


def get_typename_for_model_class(model: object, for_concrete_model=True) -> str:
    """
    Get typename for model instance.
    """
    if for_concrete_model:
        model = model._meta.concrete_model
    else:
        model = model._meta.proxy_for_model

    return "{0}.{1}".format(model._meta.app_label, model._meta.model_name)


def get_typename_for_model_instance(model_instance):
    """
    Get content type tuple from model instance.
    """
    ct = ContentType.objects.get_for_model(model_instance)
    return ".".join([ct.app_label, ct.model])


def reload_attribute(model_instance, attr_name):
    """Fetch the stored value of a model instance attribute.

    :param model_instance: Model instance.
    :param attr_name: Attribute name to fetch.
    """
    qs = type(model_instance).objects.filter(id=model_instance.id)
    return qs.values_list(attr_name, flat=True)[0]


