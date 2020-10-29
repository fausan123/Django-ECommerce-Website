from django.contrib import admin
from .models import AuctionListing, Bids, AuctionComment, User
# Register your models here.

admin.site.register(User)
admin.site.register(AuctionListing)
admin.site.register(Bids)
admin.site.register(AuctionComment)
