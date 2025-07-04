"""
Django settings for mysite project.

Generated by 'django-admin startproject' using Django 5.2.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.2/ref/settings/
"""

from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-pa=l1i$)u)wlx((%8pj41-*uc$)%z$knwmu5$s8w+n09mz+&yg'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['192.168.100.17', '127.0.0.1', 'localhost', '*']

SITE_ID = 1


# Application definition

INSTALLED_APPS = [
    'tailwind',
    'theme',
    'django_browser_reload',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'a_classroom.apps.AClassroomConfig',
    'b_enrollment.apps.BEnrollmentConfig',
    'c_activities.apps.CActivitiesConfig',
    'd_compiler.apps.DCompilerConfig',
    'register.apps.RegisterConfig',
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
]

TAILWIND_APP_NAME = 'theme'
NPM_BIN_PATH = "C:/Program Files/nodejs/npm.cmd"

SOCIALACCOUNT_PROVIDERS = {
    'google' : {
        'SCOPE' : [
            'profile',
            'email'
        ],
        'AUTH_PARAMS' : {
            'access_type' : 'online'
        }
    }
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # below is the middleware from register app
    'register.middleware.NoCacheMiddleware',
    'register.middleware.RedirectAuthenticatedUserMiddleware',
    # below is the middleware for allowing user to login with their google account
    'allauth.account.middleware.AccountMiddleware',
    # below is the middleware for the django browser reload
    'django_browser_reload.middleware.BrowserReloadMiddleware',
    # below is the middleware for the whitenoise
    'whitenoise.middleware.WhiteNoiseMiddleware',
]

ROOT_URLCONF = 'mysite.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'mysite.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/
STATIC_ROOT = BASE_DIR / "productionfiles"
STATICFILES_DIRS = [
    BASE_DIR / 'static'
]
STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
LOGIN_REDIRECT_URL = '/classroom/'
LOGOUT_REDIRECT_URL = '/login/'
#api key for the compiler
JUDGE0_URL = "https://judge0-ce.p.rapidapi.com/submissions"
HEADERS = {
    "X-RapidAPI-Key": "504f5f8347mshfddb83bb53d2821p1f2430jsne3a1f53c5a1b",
    "X-RapidAPI-Host": "judge0-ce.p.rapidapi.com"
}
#configuration for allowing user to login with google or email account
AUTHENTICATION_BACKENDS = {
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend'
}
ACCOUNT_ADAPTER = "allauth.account.adapter.DefaultAccountAdapter"
ACCOUNT_SIGNUP_FIELDS = ["email*", "password1*", "password2*"]
ACCOUNT_SIGNUP_REDIRECT_URL = "/"
ACCOUNT_LOGIN_METHODS = {"email"}
#configuration for sending an email
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = "codecheckai@gmail.com"
EMAIL_HOST_PASSWORD = "dzon ahym luyw naof"
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
#configuration for allowing the user to upload and display an image
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'