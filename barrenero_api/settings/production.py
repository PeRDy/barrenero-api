"""
Production settings
"""
import os

from barrenero_api.settings.base import Base

__all__ = ['Production']


class Production(Base):
    DEBUG = False

    # Check providers for django-status
    HEALTH_CHECK_PROVIDERS = {
        'health': (
            ('ping', 'health_check.providers.health.ping', None, None),
            ('databases', 'health_check.providers.django.health.databases', None, None),
        ),
    }

    CLINNER_DEFAULT_ARGS = {
        'runserver': '0.0.0.0:8000',
        'passenger': '--environment production '
                     '--log-file /srv/apps/barrenero-api/logs/passenger.log '
                     '--python python3.6 '
                     '--app-type wsgi '
                     '--startup-file barrenero_api/wsgi.py',
        'unit_tests': '--no-input',
    }

    @classmethod
    def pre_setup(cls):
        super(Production, cls).pre_setup()

        os.environ['DJANGO_SECRET_KEY'] = os.environ.get('DJANGO_SECRET_KEY', '1234567890')

        cls.REQUEST_LOGGING_EXCLUDE[''] += (r'{}'.format(cls.STATIC_URL),)

        # Disable logging
        cls.LOGGING['handlers']['console']['class'] = 'logging.NullHandler'
