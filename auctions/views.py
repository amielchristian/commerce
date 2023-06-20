from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
from django.core.validators import MinValueValidator

from .models import Listing, User, Bid

class PlaceBidForm(forms.Form):
    bid_amount = forms.DecimalField(label="", max_digits=9, decimal_places=2, max_value=999999999.99)

    def __init__(self, *args, **kwargs):
        min_value = kwargs.pop('min_value', None)
        super().__init__(*args, **kwargs)
        if min_value is not None:
            self.fields['bid_amount'].widget.attrs['min'] = min_value


def index(request):
    listings = Listing.objects.filter(is_active=True).all()

    return render(request, "auctions/index.html", {
        "listings": listings
    })

def listing(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)
    bids = listing.bids.all()
    bid_amount = len(bids)
    minimum_bid = listing.start_price
    if listing.start_price < listing.highest_bid():
        minimum_bid = float(listing.highest_bid())+0.01

    # handle form
    if request.method == "POST":
        form = PlaceBidForm(request.POST)

        # check if user is logged in
        if request.user.is_authenticated:
            if form.is_valid():
                bid_amount = form.cleaned_data["bid_amount"] # isolate the bid amount from the cleaned form data

                # check if bid amount is a valid bid amount  
                if bid_amount >= minimum_bid:              
                    bid = Bid(bidder=request.user, bid=bid_amount, listing=listing) # create bid object
                    bid.save() # save the object, inserting it to the database
                    listing.bids.add(bid) # add bid to bids
                    
                return HttpResponseRedirect(reverse(f"listing", args=[listing_id])) # redirect to listing page

    
    return render(request, "auctions/listing.html", {
        "bid_form": PlaceBidForm(min_value = minimum_bid),
        "listing_id": listing_id,
        "listing": listing,
        "bids": bids,
        "bid_amount": bid_amount
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