# -*- coding: utf-8 -*-
from django.contrib.auth import get_user_model
from rest_framework import exceptions as exc
from django.shortcuts import reverse
from django.apps import apps
from django.core import signing
from django.utils.translation import ugettext as _

def get_token_for_user(user, scope):
    """
    Generate a new signed token containing
    a specified user limited for a scope (identified as a string).
    """
    data = {"user_%s_id" % (scope): user.id}
    return signing.dumps(data)

def get_user_for_token(token, scope, max_age=None):
    """
    Given a selfcontained token and a scope try to parse and
    unsign it.

    If max_age is specified it checks token expiration.

    If token passes a validation, returns
    a user instance corresponding with user_id stored
    in the incoming token.
    """
    try:
        data = signing.loads(token, max_age=max_age)
    except signing.BadSignature:
        raise exc.NotAuthenticated(_("Invalid token"))

    model_cls = get_user_model()

    try:
        user = model_cls.objects.get(pk=data["user_%s_id" % (scope)])
    except (model_cls.DoesNotExist, KeyError):
        raise exc.NotAuthenticated(_("Invalid token"))
    else:
        return user

def get_token_for_settlement(settlement, scope):
    """
    Generate a new signed token containing
    a specified user limited for a scope (identified as a string).
    """
    data = {"settlement_%s_id" % (scope): settlement.id}
    return signing.dumps(data)

def get_settlement_for_token(token, scope, max_age=None):
    """
    Given a selfcontained token and a scope try to parse and
    unsign it.

    If max_age is specified it checks token expiration.

    If token passes a validation, returns
    a user instance corresponding with user_id stored
    in the incoming token.
    """
    try:
        data = signing.loads(token, max_age=max_age)
    except signing.BadSignature:
        raise exc.NotAuthenticated(_(" Your confirmation link has either expired or is invalid.<br> <a href='{0}'>Please try updating your settings again.</a> ".format(reverse('pesaify-account-settlement'))))

    return data["settlement_%s_id" % (scope)]
