from django.conf.urls import include, url

from core.views import ether, restart, status, storj, wallet
from core.views.auth import ObtainUser, UserRegister

auth_patterns = (
    [
        url(r'user/?$', ObtainUser.as_view(), name='token'),
        url(r'register/?$', UserRegister.as_view(), name='register'),
    ],
    'auth')

ether_patterns = (
    [
        url(r'nanopool/?$', ether.Nanopool.as_view(), name='nanopool'),
        url(r'status/?$', ether.Status.as_view(), name='nanopool'),
    ],
    'ether')

urlpatterns = [
    url(r'ether/', include(ether_patterns)),
    url(r'auth/', include(auth_patterns)),
    url(r'status/?', status.Status.as_view(), name='status'),
    url(r'storj/?', storj.Storj.as_view(), name='storj'),
    url(r'restart/?', restart.RestartService.as_view(), name='restart'),
    url(r'wallet/?', wallet.Wallet.as_view(), name='wallet'),
]
