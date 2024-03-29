# -*- coding: utf-8 -*-
from django.contrib.sitemaps import Sitemap as DjangoSitemap
from django.utils.translation import get_language, activate


class Sitemap(DjangoSitemap):
    """
    A language-specific Sitemap class. Returns URLS for items for passed
    language.
    """
    def __init__(self, language):
        self.language = language
        self.original_language = get_language()
        activate(self.original_language)

    def get_urls(self, page=1, site=None):
        urls = []
        latest_lastmod = None
        all_items_lastmod = True  # track if all items have a lastmod
        for item in self.paginator.page(page).object_list:
            loc = self.__get('location', item)
            priority = self.__get('priority', item, None)
            lastmod = self.__get('lastmod', item, None)
            if all_items_lastmod:
                all_items_lastmod = lastmod is not None
                if (all_items_lastmod and
                        (latest_lastmod is None or lastmod > latest_lastmod)):
                    latest_lastmod = lastmod
            url_info = {
                'item': item,
                'location': loc,
                'lastmod': lastmod,
                'changefreq': self.__get('changefreq', item, None),
                'priority': str(priority if priority is not None else ''),
            }
            urls.append(url_info)
        if all_items_lastmod and latest_lastmod:
            self.latest_lastmod = latest_lastmod

        return urls
