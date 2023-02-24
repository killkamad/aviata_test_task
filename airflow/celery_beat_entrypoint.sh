#!/bin/sh

until cd /code
do
    echo "Waiting for airflow volume..."
done

cd airflow || exit
echo "from airflow.celery_tasks import download_updates_from_national_bank_daily; download_updates_from_national_bank_daily.delay()" | python manage.py shell || true
celery -A airflow beat --loglevel=info
