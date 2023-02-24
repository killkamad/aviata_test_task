#!/bin/sh

until cd /code
do
    echo "Waiting for airflow volume..."
done

cd airflow || exit
celery -A airflow worker --loglevel=info