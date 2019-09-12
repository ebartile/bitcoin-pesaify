import datetime
from django_jinja import library
from django_sites import get_by_id as get_site_by_id
from django import template
from django.shortcuts import reverse

register = template.Library()

@library.global_function(name="resolve_url")
def resolve(type, *args):
    site = get_site_by_id("front")
    url_tmpl = "{scheme}//{domain}{url}"

    scheme = site.scheme and "{0}:".format(site.scheme) or ""
    url = reverse(type, args=list(args))
    return url_tmpl.format(scheme=scheme, domain=site.domain, url=url)

@register.filter()
def subtractdays(days):
   newDate = datetime.date.today() - datetime.timedelta(days=days)
   return newDate
