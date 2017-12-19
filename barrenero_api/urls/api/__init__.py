from django.urls import include, path

urlpatterns = [
    path('v1/', include(('barrenero_api.urls.api.v1', 'v1'), namespace='v1')),
]
