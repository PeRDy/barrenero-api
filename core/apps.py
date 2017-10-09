from django.apps import AppConfig
from django.conf import settings
from django.db.models.signals import post_save


class CoreConfig(AppConfig):
    name = 'core'
    verbose_name = 'Core'

    def ready(self):
        from core.signals.handlers import create_auth_token
        post_save.connect(create_auth_token, sender=settings.AUTH_USER_MODEL)
