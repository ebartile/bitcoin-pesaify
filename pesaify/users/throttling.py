# -*- coding: utf-8 -*-
from rest_framework import throttling
from pesaify.base import throttling as throt

class UserDetailRateThrottle(throt.GlobalThrottlingMixin,throt.ThrottleByActionMixin, throttling.SimpleRateThrottle):
    scope = "user-detail"
    throttled_actions = ["by_username", "retrieve"]


class UserUpdateRateThrottle(throt.ThrottleByActionMixin, throttling.UserRateThrottle):
    scope = "user-update"
    throttled_actions = ["update", "partial_update"]

class RegisterFailRateThrottle(throttling.AnonRateThrottle):
    scope = "register-fail"
