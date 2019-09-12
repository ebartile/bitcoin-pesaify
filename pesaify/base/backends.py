# -*- coding: utf-8 -*-

"""
Authentication backends for rest framework.

This module exposes two backends: session and token.

The first (session) is a modified version of standard
session authentication backend of restframework with
csrf token disabled.

And the second (token) implements own version of oauth2
like authentiacation but with selfcontained tokens. Thats
makes authentication totally stateles.

It uses django signing framework for create new
selfcontained tokens. This trust tokes from external
fraudulent modifications.
"""

import re

from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from .tokens import get_user_for_token

class ApiToken(BaseAuthentication):
    """
    Self-contained stateles authentication implementatrion
    that work similar to oauth2.
    It uses django signing framework for trust data stored
    in the token.
    Clients should authenticate by passing the token key in the "Authorization"
    HTTP header, prepended with the string "Bearer ".  For example:

        Authorization: Bearer 401f7ac837da42b97f613d789819ff93537bee6a

    """

    auth_rx = re.compile(r"^Bearer (.+)$")

    def authenticate(self, request):
        if "HTTP_AUTHORIZATION" not in request.META:
            return None

        token_rx_match = self.auth_rx.search(request.META["HTTP_AUTHORIZATION"])
        if not token_rx_match:
            return None

        token = token_rx_match.group(1)

        user = get_user_for_token(token, "token",
                                  max_age=None)

        return (user, token)

    def authenticate_header(self, request):
        return 'Bearer realm="api"'

class Token(BaseAuthentication):
    """
    Self-contained stateles authentication implementatrion
    that work similar to oauth2.
    It uses django signing framework for trust data stored
    in the token.
    Clients should authenticate by passing the token key in the "Authorization"
    HTTP header, prepended with the string "Bearer ".  For example:

        Authorization: Bearer 401f7ac837da42b97f613d789819ff93537bee6a

    """

    auth_rx = re.compile(r"^Bearer (.+)$")

    def authenticate(self, request):
        if "HTTP_AUTHORIZATION" not in request.META:
            return None

        token_rx_match = self.auth_rx.search(request.META["HTTP_AUTHORIZATION"])
        if not token_rx_match:
            return None

        token = token_rx_match.group(1)
        max_age_auth_token = getattr(settings, "MAX_AGE_AUTH_TOKEN", None)
        user = get_user_for_token(token, "authentication",
                                  max_age=max_age_auth_token)

        return (user, token)

    def authenticate_header(self, request):
        return 'Bearer realm="api"'
