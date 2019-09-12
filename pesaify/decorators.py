from functools import wraps
from django.shortcuts import render,reverse, redirect
from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _
from django.contrib.auth import REDIRECT_FIELD_NAME

import requests

def check_recaptcha(view_func):
    @wraps(view_func)
    def _wrapped_view(view, request, *args, **kwargs):
        request.recaptcha_is_valid = None
        recaptcha_response = request.data.get('g-recaptcha-response', None)
        data = {
            'secret': settings.GOOGLE_RECAPTCHA_SECRET_KEY,
            'response': recaptcha_response
        }
        try:
            r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
            result = r.json()
        except ValidationError:
            raise ValidationError(_("Failed to establish a new connection"))

        if result['success']:
            request.recaptcha_is_valid = True
        else:
            request.recaptcha_is_valid = False
        return view_func(view, request, *args, **kwargs)
    return _wrapped_view

def login_forbidden(view_func):
    """
    Only allow anonymous users to access this view.
    """
    @wraps(view_func)
    def _checklogin(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return view_func(self, request, *args, **kwargs)
        redirect_to = request.GET.get("next", None)
        if redirect is None:
            return redirect(redirect_to)
        else:
            return redirect(reverse('pesaify-dashboard'))

    return _checklogin

def login_forbidden_class(view_func):
    """
    Only allow anonymous users to access this view.
    """
    @wraps(view_func)
    def _checklogin(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return view_func(request, *args, **kwargs)
        redirect_to = request.GET.get("next", None)
        if redirect is None:
            return redirect(redirect_to)
        else:
            return redirect(reverse('pesaify-dashboard'))

    return _checklogin

def login_required(view_func):
    """
    Only allow anonymous users to access this view.
    """
    @wraps(view_func)
    def _checklogin(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return view_func(self, request, *args, **kwargs)

        redirect_to = request.GET.get("next", request.path)

        return redirect(reverse(settings.LOGIN_URL) + '?next='+redirect_to)

    return _checklogin

def login_required_class(view_func):
    """
    Only allow anonymous users to access this view.
    """
    @wraps(view_func)
    def _checklogin(request, *args, **kwargs):
        if request.user.is_authenticated:
            return view_func(request, *args, **kwargs)

        redirect_to = request.GET.get("next", request.path)

        return redirect(reverse(settings.LOGIN_URL) + '?next='+redirect_to)

    return _checklogin


