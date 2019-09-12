# -*- coding: utf-8 -*-

from .generics import GenericSitemap

from django.conf import settings

language_neutral_sitemaps = {
    "generics": GenericSitemap,

}

base_sitemaps = {}
for language, __ in settings.LANGUAGES:
    for name, sitemap_class in language_neutral_sitemaps.items():
        base_sitemaps['{0}-{1}'.format(name, language)] = sitemap_class(language)

sitemaps = base_sitemaps
