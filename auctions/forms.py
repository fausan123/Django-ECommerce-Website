from django import forms
from .models import Bids, AuctionComment, AuctionListing


class CreateForm(forms.ModelForm):
    class Meta:
        model = AuctionListing
        fields = ["title", "description", "price", "image", "category"]


class BidForm(forms.ModelForm):
    bid = forms.FloatField(label="")

    class Meta:
        model = Bids
        fields = ['bid']


class CommentForm(forms.ModelForm):
    comment = forms.CharField(
        label="", widget=forms.Textarea(attrs={'rows': 3}))

    class Meta:
        model = AuctionComment
        fields = ['comment']
