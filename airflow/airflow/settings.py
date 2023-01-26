"""
Django settings for airflow project.

Generated by 'django-admin startproject' using Django 3.2.13.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

import os
import sys
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(os.path.abspath(BASE_DIR.parent))  # adding main folder with base_setting file
from base_settings import *
from utils import download_currency_rates_daily
from apscheduler.triggers.cron import CronTrigger
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-6=w8j+=v$m-n#1l(hp96_$n+(9!oxs)+=sp0ex=p)pdu^f-1i7'

# SECURITY WARNING: don't run with debug turned on in production!

ROOT_URLCONF = 'airflow.urls'

WSGI_APPLICATION = 'airflow.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/",
        "KEY_PREFIX": "airflow",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

CELERY_BROKER_URL = 'redis://localhost:6379/1'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/1'

# Everyday at 12 pm, currencies will be updated
scheduler = AsyncIOScheduler()
trigger = CronTrigger(
    year="*", month="*", day="*", hour="12", minute="0", second="*"
)
scheduler.start()
scheduler.add_job(
    download_currency_rates_daily,
    trigger=trigger,
    name='download_currency_rates'
)