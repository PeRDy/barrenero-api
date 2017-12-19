from django.urls import include, path

from core.views import ether, restart, status, storj, wallet
from core.views.auth import ObtainUser, UserRegister

auth_patterns = (
    [
        path('user/', ObtainUser.as_view(), name='token'),
        path('register/', UserRegister.as_view(), name='register'),
    ],
    'auth')

ether_patterns = (
    [
        path('nanopool/', ether.Nanopool.as_view(), name='nanopool'),
        path('status/', ether.Status.as_view(), name='status'),
    ],
    'ether')

urlpatterns = [
    path('ether/', include(ether_patterns)),
    path('auth/', include(auth_patterns)),
    path('status/', status.Status.as_view(), name='status'),
    path('storj/', storj.Storj.as_view(), name='storj'),
    path('restart/', restart.RestartService.as_view(), name='restart'),
    path('wallet/', wallet.Wallet.as_view(), name='wallet'),
]
