from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.db import models
from django.urls import reverse
from django.core.exceptions import ValidationError


class User(AbstractUser):
    pass


class AuctionListing(models.Model):
    title = models.CharField(max_length=64)
    price = models.FloatField()
    description = models.TextField()
    date = models.DateTimeField(default=timezone.now)
    image = models.ImageField(
        upload_to='auction_pics/', blank=True, default='default.jpg')
    category = models.CharField(
        max_length=16, blank=True)
    active = models.BooleanField(default=True)
    watchlist = models.ManyToManyField(
        User, related_name='watchlists')
    creator = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="listings")

    def __str__(self):
        return f'{self.title} - {self.creator}'

    def get_absolute_url(self):
        return reverse('index')


class Bids(models.Model):
    bid = models.FloatField()
    listing = models.ForeignKey(
        AuctionListing, on_delete=models.CASCADE, related_name="bids")
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="bids")

    def __str__(self):
        return f'${self.bid} on ({self.listing}) by {self.user}'


class AuctionComment(models.Model):
    comment = models.TextField()
    listing = models.ForeignKey(
        AuctionListing, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="comments")

    def __str__(self):
        return f'"{self.comment}" on ({self.listing}) by {self.user}'
