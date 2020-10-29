from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from .models import User, AuctionListing, AuctionComment, Bids
from .forms import BidForm, CommentForm, CreateForm


def index(request):
    listings = AuctionListing.objects.filter(active=True).order_by('-date')
    return render(request, "auctions/index.html", {
        "listings": listings
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


@login_required
def createlisting(request):
    if request.method == 'POST':
        form = CreateForm(request.POST, request.FILES)
        if form.is_valid():
            title = form.cleaned_data['title']
            description = form.cleaned_data['description']
            price = form.cleaned_data['price']
            image = form.cleaned_data['image']
            category = form.cleaned_data['category']
            if not category and image == 'default.jpg':
                return render(request, "auctions/auctionlisting.html", {
                    "form": CreateForm(),
                    "message": "Both Image and Category cannot be empty. Please fill any one."
                })
            listing = AuctionListing.objects.create(title=title, description=description, price=price,
                                                    image=image, category=category, creator=request.user)
            listing.save()
            return redirect('index')
    return render(request, "auctions/auctionlisting.html", {
        "form": CreateForm()
    })


def listing(request, listing_id):
    listing = AuctionListing.objects.get(id=listing_id)
    bids = Bids.objects.filter(listing=listing)
    comments = AuctionComment.objects.filter(listing=listing)
    if request.method == 'POST':
        bid_form = BidForm(request.POST)
        comment_form = CommentForm(request.POST)
        active = request.POST.get('active')
        watchlist = request.POST.get('watchlist')
        if active:
            listing.active = False
            listing.save()
            return redirect('index')
        if watchlist:
            if request.user in listing.watchlist.all():
                listing.watchlist.remove(request.user)
            else:
                listing.watchlist.add(request.user)
            listing.save()
            return redirect(reverse('listing', kwargs={'listing_id': listing.id}))
        if bid_form.is_valid():
            bid = bid_form.cleaned_data['bid']
            if bid == listing.price and len(bids.all()) == 0:
                new_price = Bids.objects.create(
                    bid=bid, listing=listing, user=request.user)
                listing.price = bid
                listing.save()
                new_price.save()
            elif bid <= listing.price:
                return render(request, "auctions/listing.html", {
                    "listing": listing, "comments": comments, "bids": bids,
                    "bid_form": bid_form, "comment_form": comment_form,
                    "message": "Your bid is less than the current price"
                })
            else:
                new_price = Bids.objects.create(
                    bid=bid, listing=listing, user=request.user)
                listing.price = bid
                listing.save()
                new_price.save()
        if comment_form.is_valid():
            comment = comment_form.cleaned_data['comment']
            new_comment = AuctionComment(
                comment=comment, listing=listing, user=request.user)
            new_comment.save()
    currentbid = None
    for bid in bids:
        if bid.bid == listing.price and bid.user == request.user and not listing.active:
            currentbid = request.user
        else:
            currentbid = None
        if bid.bid > listing.price:
            listing.price = bid.bid
            listing.save()
    bid_form = BidForm()
    comment_form = CommentForm()
    return render(request, "auctions/listing.html", {
        "listing": listing, "comments": comments, "bids": bids,
        "bid_form": bid_form, "comment_form": comment_form, "currentbid": currentbid,
    })


@login_required
def watchlist(request):
    listings = AuctionListing.objects.filter(
        watchlist=request.user).order_by('-date')
    return render(request, "auctions/watchlist.html", {
        "listings": listings
    })


def categorylist(request):
    categories = set()
    listings = AuctionListing.objects.all()
    for listing in listings:
        categories.add(listing.category)
    categories = list(categories)
    return render(request, "auctions/categorylist.html", {
        "categories": categories
    })


def category_view(request, category):
    listings = AuctionListing.objects.filter(
        category=category, active=True).order_by('-date')
    return render(request, "auctions/category.html", {
        "listings": listings, "category": category
    })
