# -*- coding: utf-8 -*-
from django.db.models import Q
from django.apps import apps

from pesaify.base.templatetags.functions import resolve

from .base import Sitemap


class GenericSitemap(Sitemap):
    protocol = "https"

    def items(self):
        return [
            {"url_key": "two_factor:login", "changefreq": "monthly", "priority": 1},
            {"url_key": "pesaify-signup", "changefreq": "monthly", "priority": 1},
            {"url_key": "pesaify-forgot-password", "changefreq": "monthly", "priority": 1},
        ]

    def location(self, obj):
        return resolve(obj["url_key"])

    def changefreq(self, obj):
        return obj.get("changefreq", None)

    def priority(self, obj):
        return obj.get("priority", None)

