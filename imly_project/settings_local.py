import os
PROJECT_DIR = os.path.abspath(os.path.dirname(__file__))
DEBUG=True # also defined in settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'igeo',                      # Or path to database file if using sqlite3.
        # The following settings are not used with sqlite3:
        'USER': 'manish',
        'PASSWORD': 'manish',
        'HOST': 'localhost',                      # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': '',                      # Set to empty string for default.
    }
}
ALLOWED_HOSTS = []
STATIC_URL = '/static/'
#make crispy forms fail loudly in debug mode
CRISPY_FAIL_SILENTLY = not DEBUG
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
