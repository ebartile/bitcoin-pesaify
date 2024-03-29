# -*- coding: utf-8 -*-

from django import http
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin

COORS_ALLOWED_ORIGINS = "*"
COORS_ALLOWED_METHODS = ["POST", "GET", "OPTIONS", "PUT", "DELETE", "PATCH", "HEAD"]
COORS_ALLOWED_HEADERS = ["content-type", "x-requested-with",
                         "authorization", "accept-encoding",
                         "x-disable-pagination", "x-lazy-pagination",
                         "x-host", "x-session-id", "set-orders"]
COORS_ALLOWED_CREDENTIALS = True
COORS_EXPOSE_HEADERS = ["x-pagination-count", "x-paginated", "x-paginated-by",
                        "x-pagination-current", "x-pagination-next", "x-pagination-prev",
                        "x-site-host", "x-site-register"]

COORS_EXTRA_EXPOSE_HEADERS = getattr(settings, "APP_EXTRA_EXPOSE_HEADERS", [])


class CoorsMiddleware(MiddlewareMixin):

    def _populate_response(self, response):
        response["Access-Control-Allow-Origin"] = COORS_ALLOWED_ORIGINS
        response["Access-Control-Allow-Methods"] = ",".join(COORS_ALLOWED_METHODS)
        response["Access-Control-Allow-Headers"] = ",".join(COORS_ALLOWED_HEADERS)
        response["Access-Control-Expose-Headers"] = ",".join(COORS_EXPOSE_HEADERS + COORS_EXTRA_EXPOSE_HEADERS)
        response["Access-Control-Max-Age"] = "3600"

        if COORS_ALLOWED_CREDENTIALS:
            response["Access-Control-Allow-Credentials"] = "true"

    def process_request(self, request):
        if "HTTP_ACCESS_CONTROL_REQUEST_METHOD" in request.META:
            response = http.HttpResponse()
            self._populate_response(response)
            return response
        return None

    def process_response(self, request, response):
        self._populate_response(response)
        return response
