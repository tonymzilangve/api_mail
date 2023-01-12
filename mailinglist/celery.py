import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mailinglist.settings")

app = Celery("mailinglist")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()

app.conf.beat_schedule = {
    'check-mail-status-every-hour': {
        'task': 'check_mail_status',
        'schedule': crontab(hour='*', minute=0),
    },
}

app.conf.beat_schedule = {
    'send-statistics-to-email': {
        'task': 'send_statistics',
        'schedule': crontab(hour=9, minute=0),
    },
}
