# -*- coding: utf-8 -*-
import sys, os
from decouple import config, Csv
from django.utils.translation import ugettext_lazy as _

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=False, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv())

APPEND_SLASH = True

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.admin",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",
    'django.contrib.postgres',
    'django.contrib.humanize',

    "pesaify",
    "pesaify.base",
    "pesaify.events",
    "pesaify.users",
    "pesaify.payment",

    'django_otp',
    'django_otp.plugins.otp_static',
    'django_otp.plugins.otp_totp',
    'two_factor',
    "djmail",
    "django_jinja",
    'cookielaw',
    "django_jinja.contrib._humanize",
    "sr",
    "rest_framework",
    "easy_thumbnails",
    'storages',
    'django_celery_results',
    'django_celery_beat',
    'django_countries',
]

MIDDLEWARE = [
    "pesaify.base.middleware.cors.CoorsMiddleware",
    "pesaify.events.middleware.SessionIDMiddleware",

    # Common middlewares
    'django.middleware.security.SecurityMiddleware',
    "django.middleware.common.CommonMiddleware",
    "django.middleware.locale.LocaleMiddleware",

    # Only needed by django admin
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_otp.middleware.OTPMiddleware',
]

ROOT_URLCONF = "pesaify.urls"

TEMPLATES = [
    {
        "BACKEND": "django_jinja.backend.Jinja2",
        "DIRS": [
            os.path.join(BASE_DIR, "templates"),
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            'context_processors': [
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.request",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
            ],
            "match_extension": ".jinja",
        }
    },
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            os.path.join(BASE_DIR, "templates"),
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            'context_processors': [
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.request",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
            ],
        }
    },
]

WSGI_APPLICATION = 'settings.wsgi.application'

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
DJMAIL_REAL_BACKEND = "django.core.mail.backends.console.EmailBackend"
DJMAIL_SEND_ASYNC = True
DJMAIL_MAX_RETRY_NUMBER = 3
DJMAIL_TEMPLATE_EXTENSION = "jinja"

DATABASES = {
    "default": {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'pesaify',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en'

TIME_ZONE = 'Africa/Nairobi'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html

# Languages we provide translations for, out of the box.
LANGUAGES = [
    ("af", "Afrikaans"),  # Afrikaans
    ("ar", "العربية‏"),  # Arabic
    ("ast", "Asturiano"),  # Asturian
    ("az", "Azərbaycan dili"),  # Azerbaijani
    ("bg", "Български"),  # Bulgarian
    ("be", "Беларуская"),  # Belarusian
    ("bn", "বাংলা"),  # Bengali
    ("br", "Bretón"),  # Breton
    ("bs", "Bosanski"),  # Bosnian
    ("ca", "Català"),  # Catalan
    ("cs", "Čeština"),  # Czech
    ("cy", "Cymraeg"),  # Welsh
    ("da", "Dansk"),  # Danish
    ("de", "Deutsch"),  # German
    ("el", "Ελληνικά"),  # Greek
    ("en", "English (US)"),  # English
    ("en-au", "English (Australia)"),  # Australian English
    ("en-gb", "English (UK)"),  # British English
    ("eo", "esperanta"),  # Esperanto
    ("es", "Español"),  # Spanish
    ("es-ar", "Español (Argentina)"),  # Argentinian Spanish
    ("es-mx", "Español (México)"),  # Mexican Spanish
    ("es-ni", "Español (Nicaragua)"),  # Nicaraguan Spanish
    ("es-ve", "Español (Venezuela)"),  # Venezuelan Spanish
    ("et", "Eesti"),  # Estonian
    ("eu", "Euskara"),  # Basque
    ("fa", "فارسی‏"),  # Persian
    ("fi", "Suomi"),  # Finnish
    ("fr", "Français"),  # French
    ("fy", "Frysk"),  # Frisian
    ("ga", "Irish"),  # Irish
    ("gl", "Galego"),  # Galician
    ("he", "עברית‏"),  # Hebrew
    ("hi", "हिन्दी"),  # Hindi
    ("hr", "Hrvatski"),  # Croatian
    ("hu", "Magyar"),  # Hungarian
    ("ia", "Interlingua"),  # Interlingua
    ("id", "Bahasa Indonesia"),  # Indonesian
    ("io", "IDO"),  # Ido
    ("is", "Íslenska"),  # Icelandic
    ("it", "Italiano"),  # Italian
    ("ja", "日本語"),  # Japanese
    ("ka", "ქართული"),  # Georgian
    ("kk", "Қазақша"),  # Kazakh
    ("km", "ភាសាខ្មែរ"),  # Khmer
    ("kn", "ಕನ್ನಡ"),  # Kannada
    ("ko", "한국어"),  # Korean
    ("lb", "Lëtzebuergesch"),  # Luxembourgish
    ("lt", "Lietuvių"),  # Lithuanian
    ("lv", "Latviešu"),  # Latvian
    ("mk", "Македонски"),  # Macedonian
    ("ml", "മലയാളം"),  # Malayalam
    ("mn", "Монгол"),  # Mongolian
    ("mr", "मराठी"),  # Marathi
    ("my", "မြန်မာ"),  # Burmese
    ("nb", "Norsk (bokmål)"),  # Norwegian Bokmal
    ("ne", "नेपाली"),  # Nepali
    ("nl", "Nederlands"),  # Dutch
    ("nn", "Norsk (nynorsk)"),  # Norwegian Nynorsk
    ("os", "Ирон æвзаг"),  # Ossetic
    ("pa", "ਪੰਜਾਬੀ"),  # Punjabi
    ("pl", "Polski"),  # Polish
    ("pt", "Português (Portugal)"),  # Portuguese
    ("pt-br", "Português (Brasil)"),  # Brazilian Portuguese
    ("ro", "Română"),  # Romanian
    ("ru", "Русский"),  # Russian
    ("sk", "Slovenčina"),  # Slovak
    ("sl", "Slovenščina"),  # Slovenian
    ("sq", "Shqip"),  # Albanian
    ("sr", "Српски"),  # Serbian
    ("sr-latn", "srpski"),  # Serbian Latin
    ("sv", "Svenska"),  # Swedish
    ("sw", "Kiswahili"),  # Swahili
    ("ta", "தமிழ்"),  # Tamil
    ("te", "తెలుగు"),  # Telugu
    ("th", "ภาษาไทย"),  # Thai
    ("tr", "Türkçe"),  # Turkish
    ("tt", "татар теле"),  # Tatar
    ("udm", "удмурт кыл"),  # Udmurt
    ("uk", "Українська"),  # Ukrainian
    ("ur", "اردو‏"),  # Urdu
    ("vi", "Tiếng Việt"),  # Vietnamese
    ("zh-hans", "中文(简体)"),  # Simplified Chinese
    ("zh-hant", "中文(香港)"),  # Traditional Chinese
]

# Languages using BiDi (right-to-left) layout
LANGUAGES_BIDI = ["he", "ar", "fa", "ur"]

LOCALE_PATHS = (
    os.path.join(BASE_DIR, "pesaify", "locale"),
)

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

MEDIA_URL = "/media/"
STATIC_URL = "/static/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")
# STATIC_ROOT = os.path.join(BASE_DIR, "static")

STATICFILES_DIRS = (
   os.path.join(BASE_DIR, "static"),
)

# Default configuration for reverse proxy
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Errors report configuration
SEND_BROKEN_LINK_EMAILS = True
IGNORABLE_404_ENDS = (".php", ".cgi")
IGNORABLE_404_STARTS = ("/phpmyadmin/",)

ATOMIC_REQUESTS = True

SITES = {
    "front": {"domain": "localhost:8000", "scheme": "http", "name": "front"},
}

SITE_ID = "front"

# Session configuration (only used for admin)
SESSION_ENGINE = "django.contrib.sessions.backends.db"
SESSION_COOKIE_AGE = 1209600 # (2 weeks)

# Events backend
EVENTS_PUSH_BACKEND = "pesaify.events.backends.rabbitmq.EventsPushBackend"
EVENTS_PUSH_BACKEND_OPTIONS = {"url": "amqp://guest:guest@localhost:5672//"}

# Message System
MESSAGE_STORAGE = "django.contrib.messages.storage.session.SessionStorage"

FILE_UPLOAD_PERMISSIONS = 0o644

LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
    "filters": {
        "require_debug_false": {
            "()": "django.utils.log.RequireDebugFalse"
        }
    },
    "formatters": {
        "complete": {
            "format": "%(levelname)s:%(asctime)s:%(module)s %(message)s"
        },
        "simple": {
            "format": "%(levelname)s:%(asctime)s: %(message)s"
        },
        "null": {
            "format": "%(message)s",
        },
        "django.server": {
            "()": "django.utils.log.ServerFormatter",
            "format": "[%(server_time)s] %(message)s",
        },
    },
    "handlers": {
        "null": {
            "level":"DEBUG",
            "class":"logging.NullHandler",
        },
        "console":{
            "level":"DEBUG",
            "class":"logging.StreamHandler",
            "formatter": "simple",
        },
        "mail_admins": {
            "level": "ERROR",
            "filters": ["require_debug_false"],
            "class": "django.utils.log.AdminEmailHandler",
        },
        "django.server": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "django.server",
        },
    },
    "loggers": {
        "django": {
            "handlers":["null"],
            "propagate": True,
            "level":"INFO",
        },
        "django.request": {
            "handlers": ["mail_admins", "console"],
            "level": "ERROR",
            "propagate": False,
        },
        "pesaify": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": False,
        },
        'two_factor': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        "django.server": {
            "handlers": ["django.server"],
            "level": "INFO",
            "propagate": False,
        }
    }
}

AUTH_USER_MODEL = "users.User"

MAX_AGE_ACTIVATE_ACCOUNT = None
MAX_AGE_AUTH_TOKEN = 24 * 60 * 60
MAX_AGE_CANCEL_ACCOUNT = 30 * 24 * 60 * 60 # 30 days in seconds
MAX_AGE_ACTIVATE_SETTLEMENT = 60 * 10

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        # Mainly used by pesaify-front
        "pesaify.base.backends.Token",

        # Mainly used by pesaify-api
        "pesaify.base.backends.ApiToken",

        # Mainly used for web.
        "rest_framework.authentication.SessionAuthentication",
    ),
    "DEFAULT_THROTTLE_RATES": {
        "anon-write": None,
        "user-write": None,
        "anon-read": None,
        "user-read": None,
        "login-fail": None,
        "register-fail": None,
        "user-detail": None,
        "user-update": None,
    },
    "DEFAULT_THROTTLE_WHITELIST": [],
    "PAGINATE_BY": 10,
    "PAGINATE_BY_PARAM": "page_size",
    "MAX_PAGINATE_BY": 1000,
    "DATETIME_FORMAT": "%d %b %Y %H:%M:%S"
}

# Extra expose header related to pesaify APP (see pesaify.base.middleware.cors=)
APP_EXTRA_EXPOSE_HEADERS = [
]

PUBLIC_REGISTER_ENABLED = True
# None or [] values in USER_EMAIL_ALLOWED_DOMAINS means allow any domain
USER_EMAIL_ALLOWED_DOMAINS = None

SEARCHES_MAX_RESULTS = 150

THN_LOGO_VERY_SMALL_SIZE = 40       # 40x40 pixels
THN_AVATAR_SIZE = 80                # 80x80 pixels
THN_AVATAR_BIG_SIZE = 300           # 300x300 pixels
THN_LOGO_SMALL_SIZE = 80            # 80x80 pixels
THN_LOGO_BIG_SIZE = 300             # 300x300 pixels
THN_TIMELINE_IMAGE_SIZE = 640       # 640x??? pixels
THN_CARD_IMAGE_WIDTH = 300          # 300 pixels
THN_CARD_IMAGE_HEIGHT = 200         # 200 pixels
THN_PREVIEW_IMAGE_WIDTH = 800       # 800 pixels

THN_LOGO_VERY_SMALL = "logo--very-small"
THN_AVATAR_SMALL = "avatar"
THN_AVATAR_BIG = "big-avatar"
THN_LOGO_SMALL = "logo-small"
THN_LOGO_BIG = "logo-big"
THN_ATTACHMENT_TIMELINE = "timeline-image"
THN_ATTACHMENT_CARD = "card-image"
THN_ATTACHMENT_PREVIEW = "preview-image"

THUMBNAIL_ALIASES = {
    "": {
        THN_LOGO_VERY_SMALL: {"size": (THN_LOGO_VERY_SMALL_SIZE, THN_LOGO_VERY_SMALL_SIZE), "crop": True},
        THN_AVATAR_SMALL: {"size": (THN_AVATAR_SIZE, THN_AVATAR_SIZE), "crop": True},
        THN_AVATAR_BIG: {"size": (THN_AVATAR_BIG_SIZE, THN_AVATAR_BIG_SIZE), "crop": True},
        THN_LOGO_SMALL: {"size": (THN_LOGO_SMALL_SIZE, THN_LOGO_SMALL_SIZE), "crop": True},
        THN_LOGO_BIG: {"size": (THN_LOGO_BIG_SIZE, THN_LOGO_BIG_SIZE), "crop": True},
        THN_ATTACHMENT_TIMELINE: {"size": (THN_TIMELINE_IMAGE_SIZE, 0), "crop": True},
        THN_ATTACHMENT_CARD: {"size": (THN_CARD_IMAGE_WIDTH, THN_CARD_IMAGE_HEIGHT), "crop": True},
        THN_ATTACHMENT_PREVIEW: {"size": (THN_PREVIEW_IMAGE_WIDTH, 0), "crop": False},
    },
}

CELERY_ENABLED = False
CELERY_RESULT_BACKEND = 'django-db'

# If is True /front/sitemap.xml show a valid sitemap of pesaify-front client
FRONT_SITEMAP_ENABLED = True
FRONT_SITEMAP_CACHE_TIMEOUT = 24*60*60  # In second

SR = {
    "pesaify_url": "https://www.pesaify.com",
    "social": {
        "twitter_url": "https://twitter.com/pesaify",
        "github_url": "https://github.com/pesaify",
        "instagram_url": "https://instagram.com/pesaify",
        "facebook_url": "https://facebook.com/pesaify",
    },
    "support": {
        "url": "https://www.pesaify.com/support",
        "email": "support@pesaify.com",
    }
}

# Don't commit secrets/passwords to public repository. This is just an example.
# See http://sibt.co/python-decouple
GOOGLE_RECAPTCHA_SECRET_KEY = config('GOOGLE_RECAPTCHA_SECRET_KEY')
GOOGLE_RECAPTCHA_SITE_KEY = config('GOOGLE_RECAPTCHA_SITE_KEY')

DEFAULT_CURRENCY = 'USD'

CURRENCY_FORMAT = {
    'USD': {
        'currency_digits': False,
        'format_type': "accounting",
    },
    'EUR': {
        'format': u'#,##0\xa0¤',
    }
}

LOGOUT_REDIRECT_URL = "two_factor:login"
LOGIN_URL = 'two_factor:login'
LOGIN_REDIRECT_URL = 'pesaify-dashboard'

TWO_FACTOR_PATCH_ADMIN = config('TWO_FACTOR_PATCH_ADMIN', default=False, cast=bool)
TWO_FACTOR_TOTP_DIGITS = 6
ENABLE_ADMIN = config('ENABLE_ADMIN', default=True, cast=bool)

MANAGERS = (
   ("admin@pesaify.com", "admin@pesaify.com"),
)

MERCHANT = config('MERCHANT')
BITCOIN_URL = config('BITCOIN_URL')

# NOTE: DON'T INSERT MORE SETTINGS AFTER THIS LINE
TEST_RUNNER="django.test.runner.DiscoverRunner"


if "test" in sys.argv:
    print ("\033[1;91mNo django tests.\033[0m")
    print ("Try: \033[1;33mpy.test\033[0m")
    sys.exit(0)
