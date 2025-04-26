import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_REST_API_auction_house.settings')

app = Celery('django_REST_API_auction_house')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

app.conf.beat_schedule = {
    'close-expired-auctions-every-5-minutes': {
        'task': 'auctions.tasks.close_expired_auctions',
        'schedule': crontab(minute='*/5'),  # every 5 minutes
    },
}