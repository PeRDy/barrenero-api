from django.conf.urls import include, url

from barrenero_api.urls.api import v1

urlpatterns = [
    url(r'v1/', include(v1, namespace='v1')),
]
