"""
URL Configuration
"""
from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic.base import RedirectView

import core.urls

urlpatterns = [
    url(r'^backend/', include(admin.site.urls)),
    url(r'^health_check/', include('health_check.urls')),
    url(r'^favicon.ico/?$', RedirectView.as_view(url='/static/favicon.ico', permanent=True)),
    url(r'^api/', include('barrenero_api.urls.api', namespace='core')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
