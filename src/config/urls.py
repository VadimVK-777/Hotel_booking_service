"""Root URL configuration for the service."""

from django.urls import include, path, re_path

from config.error_views import json_not_found

handler404 = "config.error_views.json_not_found"
handler500 = "config.error_views.json_server_error"

urlpatterns = [
    path("", include("hotel.urls")),
    re_path(r"^.*$", json_not_found, name="not-found"),
]
