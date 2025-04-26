

from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Auction(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='auctions')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    starting_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    ends_at = models.DateTimeField()
    highest_bid = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    winner = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='won_auctions')
    is_closed = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    @property
    def status(self):
        if self.is_closed or timezone.now() >= self.ends_at:
            return 'closed'
        return 'open'

    @property
    def is_closed_check(self):
        return timezone.now() >= self.ends_at

    def close_if_expired(self):
        if self.ends_at <= timezone.now() and self.winner is None:
            highest_bid = self.bids.order_by('-amount').first()
            if highest_bid:
                self.winner = highest_bid.user
                self.save()

    def save(self, *args, **kwargs):
        # If the auction is being created, set the highest_bid to the starting price
        if not self.id:  # Only when the auction is being created (not updated)
            self.highest_bid = self.starting_price
        if self.ends_at and timezone.now() >= self.ends_at:
            self.is_closed = True
        super().save(*args, **kwargs)

class Bid(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bids')
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name='bids')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-amount']

    def clean(self):
        # Sprawdzamy, czy oferta jest większa niż aktualna najwyższa oferta
        if self.auction.ends_at < timezone.now():
            raise ValidationError("Bidding is no longer allowed. The auction has ended.")
        if self.amount <= self.auction.highest_bid:
            raise ValidationError(f"The bid must be higher than the current highest bid of {self.auction.highest_bid}")

    def __str__(self):
        return f"{self.user.username} - {self.amount}"

    def save(self, *args, **kwargs):
        # Zanim oferta zostanie zapisana, sprawdzamy walidację
        self.clean()

        # Jeżeli oferta jest większa niż dotychczasowa najwyższa, aktualizujemy ją w aukcji
        if self.amount > self.auction.highest_bid:
            self.auction.highest_bid = self.amount
            self.auction.save()

        super().save(*args, **kwargs)
