import os
PROJECT_DIR = os.path.abspath(os.path.dirname(__file__))
DEBUG=True # also defined in settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': os.path.join(PROJECT_DIR, "database.db"),                      # Or path to database file if using sqlite3.
        # The following settings are not used with sqlite3:
        'USER': 'imly',
        'PASSWORD': '',
        'HOST': 'localhost',                      # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': '',                      # Set to empty string for default.
    }
}
ALLOWED_HOSTS = []
STATIC_URL = '/static/'
#make crispy forms fail loudly in debug mode
CRISPY_FAIL_SILENTLY = not DEBUG
EMAIL_BACKEND = 'django.core.mail.backends.dummy.EmailBackend'
