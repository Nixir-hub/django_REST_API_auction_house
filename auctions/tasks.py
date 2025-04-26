from celery import shared_task
from django.utils import timezone
from .models import Auction

@shared_task
def close_expired_auctions():
    now = timezone.now()
    expired_auctions = Auction.objects.filter(is_closed=False, ends_at__lte=now)
    updated_count = expired_auctions.update(is_closed=True)
    return f"Closed {updated_count} expired auctions."