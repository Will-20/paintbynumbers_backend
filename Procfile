web: gunicorn index:app --log-file=-
worker: celery -A index.celery worker --loglevel=INFO