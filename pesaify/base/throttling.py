# -*- coding: utf-8 -*-
from ipware.ip import get_ip

class GlobalThrottlingMixin:
    """
    Define the cache key based on the user IP independently if the user is
    logged in or not.
    """
    def get_cache_key(self, request, view):
        ident = get_ip(request)

        return self.cache_format % {
            "scope": self.scope,
            "ident": ident
        }


# If you derive a class from this mixin you have to put this class previously
# to the base throttling class.
class ThrottleByActionMixin:
    throttled_actions = []

    def allow_request(self, request, view):
        if view.action in self.throttled_actions:
            return super().allow_request(request, view)
        return True

