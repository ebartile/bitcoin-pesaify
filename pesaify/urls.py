# -*- coding: utf-8 -*-
from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from .decorators import login_forbidden
from .routers import router
from two_factor.admin import AdminSiteOTPRequired
from two_factor.urls import urlpatterns as tf_urls
from two_factor.views import LoginView

##############################################
# Front sitemap
##############################################
urlpatterns = []

if settings.FRONT_SITEMAP_ENABLED:
    from django.contrib.sitemaps.views import index
    from django.contrib.sitemaps.views import sitemap
    from django.views.decorators.cache import cache_page

    from pesaify.base.front.sitemaps import sitemaps

    urlpatterns += [
        url(r"^sitemap\.xml$",
            cache_page(settings.FRONT_SITEMAP_CACHE_TIMEOUT)(index),
            {"sitemaps": sitemaps, 'sitemap_url_name': 'front-sitemap'},
            name="front-sitemap-index"),
        url(r"^sitemap-(?P<section>.+)\.xml$",
            cache_page(settings.FRONT_SITEMAP_CACHE_TIMEOUT)(sitemap),
            {"sitemaps": sitemaps},
            name="front-sitemap")
    ]

##############################################
# Default
##############################################


urlpatterns += i18n_patterns(
    url(r'^$', LoginView.as_view()),
    url(r'', include(tf_urls)),
    url(r'^', include('django.conf.urls.i18n')),
    url(r'^', include(router.urls)),
    url(r'^robots.txt$', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
)

##############################################
# Static and media files in debug mode
##############################################

if settings.DEBUG:
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    def mediafiles_urlpatterns(prefix):
        """
        Method for serve media files with runserver.
        """
        import re
        from django.views.static import serve

        return [
            url(r'^%s(?P<path>.*)$' % re.escape(prefix.lstrip('/')), serve,
                {'document_root': settings.MEDIA_ROOT})
        ]

    # Hardcoded only for development server
    urlpatterns += staticfiles_urlpatterns(prefix="/static/")
    urlpatterns += mediafiles_urlpatterns(prefix="/media/")

if settings.ENABLE_ADMIN:
    urlpatterns += i18n_patterns(
        url(r'^admin/', admin.site.urls),
    )

#if settings.TWO_FACTOR_PATCH_ADMIN:
#    admin.site.__class__ = AdminSiteOTPRequired

