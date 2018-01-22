"""
Django settings.
"""

import os

from configurations import Configuration, values

__all__ = ['Base']


class LoggingMixin:
    """
    Logging configuration.
    """
    LOG_DIR = os.path.abspath(os.environ.get('DJANGO_APP_LOG_DIR', '/srv/apps/barrenero-api/logs/api'))

    LOGGING = {
        'version': 1,
        'disable_existing_loggers': True,
        'formatters': {
            'plain': {
                'format': '[%(asctime)s.%(msecs)dZ] %(levelname)s [%(name)s:%(lineno)s] %(message)s',
                'datefmt': '%Y-%m-%dT%H:%M:%S',
            },
        },
        'handlers': {
            'console': {
                'level': 'INFO',
                'class': 'logging.StreamHandler',
                'formatter': 'plain'
            },
            'root_file': {
                'level': 'INFO',
                'class': 'logging.handlers.TimedRotatingFileHandler',
                'filename': os.path.join(LOG_DIR, 'root.log'),
                'formatter': 'plain',
                'when': 'midnight',
                'backupCount': 30,
                'utc': True
            },
            'base_file': {
                'level': 'INFO',
                'class': 'logging.handlers.TimedRotatingFileHandler',
                'filename': os.path.join(LOG_DIR, 'base.log'),
                'formatter': 'plain',
                'when': 'midnight',
                'backupCount': 30,
                'utc': True
            },
            'runserver_file': {
                'level': 'INFO',
                'class': 'logging.handlers.TimedRotatingFileHandler',
                'filename': os.path.join(LOG_DIR, 'runserver.log'),
                'formatter': 'plain',
                'when': 'midnight',
                'backupCount': 30,
                'utc': True
            },
            'security_file': {
                'level': 'INFO',
                'class': 'logging.handlers.TimedRotatingFileHandler',
                'filename': os.path.join(LOG_DIR, 'security.log'),
                'formatter': 'plain',
                'when': 'midnight',
                'backupCount': 30,
                'utc': True
            },
            'mail_admins': {
                'level': 'ERROR',
                'filters': ['require_debug_false'],
                'class': 'django.utils.log.AdminEmailHandler',
                'include_html': True,
            },
        },
        'filters': {
            'require_debug_false': {
                '()': 'django.utils.log.RequireDebugFalse',
            }
        },
        'loggers': {
            '': {
                'handlers': ['console', 'root_file', 'mail_admins'],
                'level': 'INFO',
                'propagate': True,
            },
            'core': {
                'handlers': ['console', 'base_file', 'mail_admins'],
                'level': 'INFO',
                'propagate': False,
            },
            'barrenero_api': {
                'handlers': ['console', 'base_file', 'mail_admins'],
                'level': 'INFO',
                'propagate': False,
            },
            'django.server': {
                'handlers': ['console', 'runserver_file'],
                'level': 'INFO',
                'propagate': True,
            },
            'django.security': {
                'handlers': ['console', 'security_file', 'mail_admins'],
                'level': 'INFO',
                'propagate': True,
            },
        },
    }


class Base(LoggingMixin, Configuration):
    # Build paths inside the project like this: os.path.join(BASE_DIR, ...)
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    # SECURITY WARNING: keep the secret key used in production secret!
    SECRET_KEY = values.SecretValue()

    # SECURITY WARNING: don't run with debug turned on in production!
    DEBUG = False

    ALLOWED_HOSTS = ['*']
    ADMINS = values.SingleNestedTupleValue((
        ('José Antonio Perdiguero López', 'perdy.hh@gmail.com'),
    ))

    # Application definition

    INSTALLED_APPS = (
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        # Project apps
        'barrenero_api',
        'core',
        # System utilities
        'django_extensions',
        'health_check',
        # REST
        'rest_framework',
        'rest_framework.authtoken',
    )

    MIDDLEWARE = (
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
        'django.middleware.security.SecurityMiddleware',
        'whitenoise.middleware.WhiteNoiseMiddleware',
    )

    ROOT_URLCONF = 'barrenero_api.urls'

    TEMPLATES = [
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [],
            'APP_DIRS': True,
            'OPTIONS': {
                'context_processors': [
                    'django.template.context_processors.debug',
                    'django.template.context_processors.request',
                    'django.contrib.auth.context_processors.auth',
                    'django.contrib.messages.context_processors.messages',
                ],
            },
        },
    ]

    WSGI_APPLICATION = 'barrenero_api.wsgi.application'

    # Database
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': 'config/barrenero_api.db'
        },
    }

    # Cache
    DEFAULT_CACHE_TIMEOUT = 60 * 15
    CACHES = {
        'default': {}
    }

    # Internationalization
    LANGUAGE_CODE = 'en-us'

    TIME_ZONE = 'UTC'

    USE_I18N = True

    USE_L10N = True

    USE_TZ = True

    # Static files (CSS, JavaScript, Images)
    STATIC_URL = '/static/'
    STATIC_ROOT = os.path.abspath(os.path.join(BASE_DIR, 'assets'))  # Copy files to ./barrenero_api/assets
    STATICFILES_DIRS = [
        # os.path.abspath(os.path.join(BASE_DIR, 'client', 'dist'))
    ]

    # Media files (Upload by user)
    MEDIA_ROOT = os.path.abspath(os.path.join(BASE_DIR, 'media'))  # Copy media files to ./barrenero_api/media
    MEDIA_URL = '/media/'

    # Static finders
    STATICFILES_FINDERS = (
        'django.contrib.staticfiles.finders.FileSystemFinder',
        'django.contrib.staticfiles.finders.AppDirectoriesFinder',
        # other finders..
    )
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

    # Regex expresions to exclude from logging at middleware
    REQUEST_LOGGING_EXCLUDE = {
        '': (

        ),
        'admin': (
            r'.*',
        ),
        'health_check': (
            r'.*',
        )
    }

    DEFAULT_RESPONSE_HEADERS = {
        'Link': (
            '<https://docs.sequoia.piksel.com/concepts/api/spec.html>;rel="profile"',
        ),
        'Cache-Control': (
            'no-cache',
        ),
    }

    HEALTH_CHECK_PROVIDERS = {
        'health': (
            ('ping', 'health_check.providers.health.ping', None, None),
            ('databases', 'health_check.providers.django.health.databases', None, None),
        ),
        'stats': (
            ('databases', 'health_check.providers.django.stats.databases', None, None),
        )
    }

    AUTH_USER_MODEL = 'core.User'

    REST_FRAMEWORK = {
        'DEFAULT_AUTHENTICATION_CLASSES': (
            'rest_framework.authentication.TokenAuthentication',
        ),
        'DEFAULT_PERMISSION_CLASSES': (
            'rest_framework.permissions.IsAuthenticated',
        )
    }

    # Local config
    API_SUPERUSER = values.SecretValue()

    # Third party APIs
    NANOPOOL = {
        'url': 'https://api.nanopool.org/v1/eth/',
        'worker': values.Value(environ_name='WORKER_NAME'),
        'token': None
    }
    ETHERSCAN = {
        'url': 'https://api.etherscan.io/api',
        'token': values.SecretValue(environ_name='ETHERSCAN_TOKEN'),
    }
    ETHPLORER = {
        'url': 'https://api.ethplorer.io/',
        'token': values.SecretValue(environ_name='ETHPLORER_TOKEN'),
    }

    # Number of seconds since last entry to consider ether mining inactive
    ETHER_MAX_IDLE = 300

    # Mining container names
    MINERS = {
        'barrenero-miner-ether': 'Ether',
        'barrenero-miner-storj': 'Storj',
    }

    # Storj container name to call commands with docker
    STORJ_CONTAINER_NAME = 'barrenero-miner-storj'

    # Storj API
    STORJ_API = {
        'url': 'https://api.storj.io/',
    }
