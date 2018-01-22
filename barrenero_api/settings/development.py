"""
Development settings
"""
import os

from barrenero_api.settings.base import Base

__all__ = ['Development']


class Development(Base):
    DEBUG = True

    CLINNER_DEFAULT_ARGS = {
        'runserver': '0.0.0.0:80',
        'start': '--ini /srv/apps/barrenero-api/uwsgi.ini',
        'unit_tests': '--no-input',
    }

    @classmethod
    def pre_setup(cls):
        super(Development, cls).pre_setup()

        os.environ['DJANGO_SECRET_KEY'] = os.environ.get('DJANGO_SECRET_KEY', '1234567890')

        cls.REQUEST_LOGGING_EXCLUDE[''] += (r'{}'.format(cls.STATIC_URL),)

        for handler, props in cls.LOGGING['handlers'].items():
            props['level'] = 'DEBUG'

        for logger, props in cls.LOGGING['loggers'].items():
            props['level'] = 'DEBUG'
