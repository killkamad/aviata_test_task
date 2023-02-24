from celery.schedules import crontab
from airflow.celery import app
from asgiref.sync import async_to_sync
from django.conf import settings
from utils.currencies import update_from_national_bank
from utils.search import fetch_providers_and_save_results

app.conf.beat_schedule = {
    'run-every-day-at-12-pm': {
        'task': 'airflow.celery_tasks.download_currency_rates_daily',
        'schedule': crontab(hour=12, minute=0),
    },
}

app.conf.timezone = settings.TIME_ZONE


@app.task
def download_updates_from_national_bank_daily():
    async_to_sync(update_from_national_bank)()


@app.task
def sync_fetch_providers_and_save_results(search_id, url_list):
    async_to_sync(fetch_providers_and_save_results)(search_id, url_list)