# Django settings for imly_project project.

import os
DEBUG = True
if not DEBUG:
    DEPLOY_DOMAIN = 'imly.in'
    CSRF_COOKIE_DOMAIN = SESSION_COOKIE_DOMAIN = '.' + DEPLOY_DOMAIN
TEMPLATE_DEBUG = DEBUG
PROJECT_DIR = os.path.abspath(os.path.dirname(__file__))
LOGIN_URL="/login/"
LOGIN_REDIRECT_URL = "/food/"
LOGIN_ERROR_URL = "/login-error/"

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
    ("Abhishek Singh", "abhishek3188@gmail.com"),
    ("Pavan Mishra", "pavanmishra@gmail.com"),
)

EMAIL_USE_TLS = True
EMAIL_HOST = "smtp.mandrillapp.com"
EMAIL_HOST_USER = 'pavan@imly.in'
EMAIL_HOST_PASSWORD = 'CVJY4aOOxPELFaWFfq1ekg'
EMAIL_PORT = 587
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
DEFAULT_FROM_EMAIL='Imly<hello@imly.in>'

ADMIN_EMAIL = 'Imly Admin <admin@imly.in>'
ORDERS_EMAIL = 'Imly Orders <orders@imly.in>'
STORE_EMAIL = 'Imly Store <stores@imly.in>'
SIGNUP_EMAIL = 'Imly <hello@imly.in>'

MANAGERS = ADMINS
DATABASES = {
        'default': {
            'ENGINE': 'django.contrib.gis.db.backends.postgis', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
            'NAME': 'igeo',                      # Or path to database file if using sqlite3.
            # The following settings are not used with sqlite3:
            'USER': 'igeo',
            'PASSWORD': 'imly@food13',
            'HOST': '',                      # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
            'PORT': '',                      # Set to empty string for default.
        }
    }

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = [".imly.in", 'www.imly.in', '*.imly.in']

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'Asia/Calcutta'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = os.path.join(PROJECT_DIR, "../media")

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
STATIC_ROOT = os.path.join(PROJECT_DIR, "static")

# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"

STATIC_URL = 'https://imly.s3.amazonaws.com/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    
)

# List of finder classes that know how to find static files internationalization
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 's1ms56q2v7#s0j3$le^_+w1(=-bzuwi39&an=wq#_%4m$dxr1r'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'imly.middleware.RefererMiddleware',
    'imly.middleware.SelectCityMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'imly_project.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'imly_project.wsgi.application'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(PROJECT_DIR,"templates")
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.tz',
    'django.core.context_processors.request',
    'django.contrib.messages.context_processors.messages',
    'allauth.account.context_processors.account',
    'allauth.socialaccount.context_processors.socialaccount',
    'plata.context_processors.plata_context',
    'imly.context_processors.chef_tip',
    'imly.context_processors.modal_signup',
    'imly.context_processors.select_city',
)

AUTHENTICATION_BACKENDS = (
    #'social_auth.backends.twitter.TwitterBackend',
    #'social_auth.backends.facebook.FacebookBackend',
    #'social_auth.backends.google.GoogleOAuthBackend',
    #'social_auth.backends.google.GoogleOAuth2Backend',
    #'social_auth.backends.google.GoogleBackend',
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
    
)



INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    'django.contrib.gis',
    'south',
    'reviews',
    'imly',
    'plata',
    'plata.product.stock',
    'plata.contact',
    'plata.discount',
    'plata.payment',
    'plata.shop',
    'imagekit',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    #allauth providers
    'allauth.socialaccount.providers.facebook',
    #'allauth.socialaccount.providers.google',
    'storages',
    'widget_tweaks',
    'crispy_forms',
    'rollyourown.seo',
    'django_comments',
    'autoslug',
    #'djangoratings',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
)

MESSAGE_STORAGE = "django.contrib.messages.storage.session.SessionStorage"

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
if not DEBUG:
    LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'logfile':{
            'class': 'logging.handlers.WatchedFileHandler',
            'filename': '/var/log/django/error.log'
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'django':{
            'handlers': ['logfile'],
            'level': 'ERROR',
            'propagate': False,
        },
    }
}

#Plata settings
PLATA_SHOP_PRODUCT = 'imly.Product'

PLATA_STOCK_TRACKING = True

PAYPAL = {
    'LIVE': False, # Use sandbox or live payment interface?
    'BUSINESS': 'paypal@example.com',
    }

OGONE = {
    'LIVE': False,
    'PSPID': 'abhi3188',
    'SHA1_IN': 'imlytest@food130',
    'SHA1_OUT': 'imlytest@food131',
    }

CURRENCIES = ('INR',)

PLATA_PAYMENT_MODULES = (
    'plata.payment.modules.cod.PaymentProcessor',
    #'plata.payment.modules.postfinance.PaymentProcessor',
    #'plata.payment.modules.ogone.PaymentProcessor',
    #'plata.payment.modules.paypal.PaymentProcessor',
    )


PLATA_PAYMENT_MODULE_NAMES = {"paypal" : ("Paypal and Credit Cards"),
                            "ogone" : ("Visa/Mastercard"),
                            "cod":("Pay in Cash")
                            }

#AllAuth settings

ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 5
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = "none"
ACCOUNT_EMAIL_SUBJECT_PREFIX = "Hello from Imly! "
ACCOUNT_USERNAME_REQUIRED = False

if not DEBUG:
    #for s3 storage
    STATICFILES_STORAGE = DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
    AWS_ACCESS_KEY_ID = "AKIAJLZTSZS7CQ57KK4Q"
    AWS_SECRET_ACCESS_KEY = "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"
    AWS_STORAGE_BUCKET_NAME = "imly"
    # stops IK checking S3 all the time - main reason to use IK v2 for me
    IMAGEKIT_DEFAULT_IMAGE_CACHE_BACKEND = 'imagekit.imagecache.NonValidatingImageCacheBackend'


if DEBUG:
    from settings_local import *
