from django.contrib import admin

from auctions.models import Auction, Bid

# Register your models here.
admin.site.register(Bid)
admin.site.register(Auction)
