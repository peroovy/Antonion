"""
Django settings for app project.

Generated by 'django-admin startproject' using Django 4.0.1.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""
import base64
import logging.config
import os
from datetime import timedelta
from logging import INFO, Formatter, Logger
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

from django.contrib.auth.hashers import BCryptSHA256PasswordHasher
from environ import Env

# Build paths inside the project like this: BASE_DIR / 'subdir'.
from app.internal.logging import TelegramLogHandler

BASE_DIR = Path(__file__).resolve().parent.parent

env = Env(LOGGING=(bool, False), DEBUG=(bool, False), METRICS=(bool, False))
Env.read_env()

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env("DEBUG")

ALLOWED_HOSTS = env("ALLOWED_HOSTS").split()


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "debug_toolbar",
    "app",
    "django_cleanup.apps.CleanupConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": env("POSTGRES_DB"),
        "USER": env("POSTGRES_USER"),
        "PASSWORD": env("POSTGRES_PASSWORD"),
        "HOST": env("POSTGRES_HOST"),
        "PORT": env("POSTGRES_PORT"),
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Europe/Moscow"

USE_I18N = True
USE_L10N = False

USE_TZ = True

PHONE_REGION = "RU"

DATETIME_PARSE_FORMAT = "%Y-%m-%d %H:%m:%S"
DATETIME_FORMAT = DATETIME_INPUT_FORMATS = "Y-m-d H:m:s"

# JWT Authentication

ACCESS_TOKEN_TTL = timedelta(minutes=30)
REFRESH_TOKEN_TTL = timedelta(days=10)

HASHER = BCryptSHA256PasswordHasher()
SALT = b"$2b$12$" + base64.b64encode(SECRET_KEY.encode("utf-8"))

REFRESH_TOKEN_COOKIE = "refresh_token"

# Logging

MAX_TRANSFER_DURATION_SECONDS = 5
LOGS_LIFETIME = 14

if env("LOGGING"):
    formatter = Formatter(fmt="[{levelname}][{asctime}] {message}", datefmt="%Y-%m-%d %H:%M:%S", style="{")

    bot_handler = TelegramLogHandler(token=env("LOGGING_BOT_TOKEN"), chat_id=env("LOGGING_CHANEL_ID"), level=INFO)
    bot_handler.setFormatter(formatter)

    logger = logging.getLogger()
    logger.setLevel(INFO)
    logger.addHandler(bot_handler)

    # Transfer

    transfer_file_handler = TimedRotatingFileHandler(
        os.path.join(BASE_DIR, "logs", "transfer.log"), when="midnight", backupCount=LOGS_LIFETIME
    )
    transfer_file_handler.setLevel(INFO)
    transfer_file_handler.setFormatter(formatter)

    transfer_logger = logging.getLogger("app.internal.bank.domain.services.TransferService")
    transfer_logger.propagate = False
    transfer_logger.setLevel(INFO)
    transfer_logger.addHandler(transfer_file_handler)
    transfer_logger.addHandler(bot_handler)


# Metrics

METRICS = env("METRICS")
METRICS_SERVER_PORT = 8010

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATIC_URL = "/static/"
STATIC_ROOT = "static/"

# Storage

DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"

AWS_ACCESS_KEY_ID = env("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = env("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = env("AWS_STORAGE_BUCKET_NAME")

AWS_S3_ENDPOINT_URL = "https://storage.yandexcloud.net"

MAX_SIZE_PHOTO_KB = 1024
MAX_SIZE_PHOTO_BYTES = MAX_SIZE_PHOTO_KB * 1024


# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

INTERNAL_IPS = [
    "127.0.0.1",
]

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
AUTH_USER_MODEL = "app.AdminUser"

TELEGRAM_BOT_TOKEN = env("TELEGRAM_BOT_TOKEN")
