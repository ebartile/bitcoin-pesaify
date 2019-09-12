# -*- coding: utf-8 -*-
"""
This module contains a domain logic for authentication
process. It called services because in DDD says it.

NOTE: Python doesn't have java limitations for "everytghing
should be contained in a class". Because of that, it
not uses clasess and uses simple functions.
"""
import urllib3
import json
import binascii
import hashlib
import uuid
import json
from blockchain.v2 import receive
from django.apps import apps
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.conf import settings
from django.utils.translation import ugettext as _
from django.db import transaction as tx
from django.db import IntegrityError
from pesaify.base.templatetags.functions import resolve
from easy_thumbnails.files import get_thumbnailer
from easy_thumbnails.exceptions import InvalidImageFormatError

from pesaify.base import exceptions as exc
from pesaify.base.utils.urls import get_absolute_url
from pesaify.base.mails import mail_builder
from pesaify.base.tokens import get_token_for_user
from .signals import user_registered as user_registered_signal
from . import models

def send_register_email(user) -> bool:
    """
    Given a user, send register welcome email
    message to specified user.
    """
    activation_token = get_token_for_user(user, "activate_account")
    cancel_token = get_token_for_user(user, "cancel_account")
    context = {"user": user, "cancel_token": cancel_token, 'activation_token': activation_token}
    email = mail_builder.registered_user(user, context)
    return bool(email.send())


def is_user_already_registered(*, email:str) -> (bool, str):
    """
    Checks if a specified user is already registred.

    Returns a tuple containing a boolean value that indicates if the user exists
    and in case he does whats the duplicated attribute
    """
    user_model = get_user_model()

    if user_model.objects.filter(email=email):
        return (True, _("Email is already in use."))

    return (False, None)

@tx.atomic
def public_register(password:str, email:str, first_name:str, middle_name:str, last_name:str, accepted_terms:bool, company_name:str):
    """
    Given a parsed parameters, try register a new user
    knowing that it follows a public register flow.

    This can raise `exc.IntegrityError` exceptions in
    case of conflics found.

    :returns: User
    """

    is_registered, reason = is_user_already_registered(email=email)
    if is_registered:
        raise exc.WrongArguments(reason)

    user_model = get_user_model()
    user = user_model(username=email,
                      email=email,
                      first_name=first_name,
                      middle_name=middle_name,
                      last_name=last_name,
                      accepted_terms=accepted_terms)
    user.set_password(password)

    try:
        user.save()
    except IntegrityError:
        raise exc.WrongArguments(_("Failed to register User. Please Contact Pesaify through support@pesaify.com"))

    user.business.legal_name = company_name
    user.save()
    send_register_email(user)
    user_registered_signal.send(sender=user.__class__, user=user)

    return user

def get_user_by_username_or_email(username_or_email):
    user_model = get_user_model()
    qs = user_model.objects.filter(Q(username__iexact=username_or_email) |
                                   Q(email__iexact=username_or_email))

    if len(qs) > 1:
        qs = qs.filter(Q(username=username_or_email) |
                       Q(email=username_or_email))

    if len(qs) == 0:
        raise exc.WrongArguments(_("Username or password does not matches user."))

    user = qs[0]
    return user


def get_and_validate_user(*, username: str, password: str):
    """
    Check if user with username/email exists and specified
    password matchs well with existing user password.

    if user is valid,  user is returned else, corresponding
    exception is raised.
    """

    user = get_user_by_username_or_email(username)
    if not user.check_password(password):
        raise exc.WrongArguments(_("Username or password does not matches user."))

    return user


def get_photo_url(photo):
    """Get a photo absolute url and the photo automatically cropped."""
    if not photo:
        return None
    try:
        url = get_thumbnailer(photo)[settings.THN_AVATAR_SMALL].url
        return get_absolute_url(url)
    except InvalidImageFormatError as e:
        return None

def get_user_photo_url(user):
    """Get the user's photo url."""
    if not user:
        return None
    return get_photo_url(user.photo)


def get_big_photo_url(photo):
    """Get a big photo absolute url and the photo automatically cropped."""
    if not photo:
        return None
    try:
        url = get_thumbnailer(photo)[settings.THN_AVATAR_BIG].url
        return get_absolute_url(url)
    except InvalidImageFormatError as e:
        return None

def get_user_big_photo_url(user):
    """Get the user's big photo url."""
    if not user:
        return None
    return get_big_photo_url(user.photo)

def get_user_big_passport_url(user):
    """Get the user's big passport url."""
    if not user:
        return None
    return get_big_photo_url(user.passport)

def get_user_passport_url(user):
    """Get the user's passport url."""
    if not user:
        return None
    return get_photo_url(user.passport)

def get_user_big_permit_id_front_url(user):
    """Get the user's big permit or national id url."""
    if not user:
        return None
    return get_big_photo_url(user.permit_id_front)

def get_user_big_permit_id_back_url(user):
    """Get the user's big permit or national id url."""
    if not user:
        return None
    return get_big_photo_url(user.permit_id_back)

def get_user_permit_id_front_url(user):
    """Get the user's permit or national id url."""
    if not user:
        return None
    return get_photo_url(user.permit_id_front)

def get_user_permit_id_back_url(user):
    """Get the user's permit or national id url."""
    if not user:
        return None
    return get_photo_url(user.permit_id_back)
