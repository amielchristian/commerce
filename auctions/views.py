from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms

from .models import Listing, User, Bid, Comment, Category

class PlaceBidForm(forms.Form):
    bid_amount = forms.DecimalField(label="", max_digits=9, decimal_places=2, max_value=999999999.99)

    def __init__(self, *args, **kwargs):
        min_value = kwargs.pop('min_value', None)
        super().__init__(*args, **kwargs)
        if min_value is not None:
            self.fields['bid_amount'].widget.attrs['min'] = min_value

class CommentForm(forms.Form):
    comment = forms.CharField(label = "", widget=forms.Textarea(attrs={"placeholder": "Add a comment here"}))

class CreateListingForm(forms.Form):
    name = forms.CharField(label="Name")
    category = forms.ChoiceField(choices=[(category, category) for category in Category.objects.all()])
    image = forms.ImageField(required=False)
    description = forms.CharField(widget=forms.Textarea(), required=False)
    start_price = forms.DecimalField(label="Starting Price", max_digits=9, decimal_places=2, max_value=999999999.99)

def index(request):
    listings = Listing.objects.filter(is_active=True).all()

    return render(request, "auctions/index.html", {
        "listings": listings
    })

def listing(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)
    comments = listing.comments.all().order_by("-time")
    bids = listing.bids.all()
    bid_amount = len(bids)
    minimum_bid = listing.start_price
    if listing.start_price < listing.highest_bid():
        minimum_bid = float(listing.highest_bid())+0.01

    # handle bid form
    if request.method == "POST":
        # check if user is logged in
        if request.user.is_authenticated:
            form_1 = PlaceBidForm(request.POST)
            form_2 = CommentForm(request.POST)

            if form_1.is_valid():
                if bool(form_1.cleaned_data):            
                    bid_amount = form_1.cleaned_data["bid_amount"] # isolate the bid amount from the cleaned form data

                    # check if bid amount is a valid bid amount  
                    if bid_amount >= minimum_bid:              
                        bid = Bid(bidder=request.user, bid=bid_amount, listing=listing) # create bid object
                        bid.save() # save the object, inserting it to the database
                        listing.bids.add(bid) # add bid to bids

            elif form_2.is_valid():
                if bool(form_2.cleaned_data):            
                    comment = Comment(comment=form_2.cleaned_data["comment"], commenter=request.user, listing=listing)
                    comment.save()
                    listing.comments.add(comment)

            else:
                add = request.POST.get("add")
                remove = request.POST.get("remove")

                if add is not None:
                    request.user.watchlist.add(listing)
                elif remove is not None:
                    request.user.watchlist.remove(listing)

            return HttpResponseRedirect(reverse(f"listing", args=[listing_id])) # redirect to listing page

    return render(request, "auctions/listing.html", {
        "bid_form": PlaceBidForm(min_value = minimum_bid),
        "comment_form": CommentForm(),
        "listing_id": listing_id,
        "listing": listing,
        "bids": bids,
        "comments": comments,
        "bid_amount": bid_amount,
        "in_watchlist": request.user.watchlist.filter(id=listing_id).exists()
    })

@login_required(login_url='login')
def watchlist(request):
    watchlist = request.user.watchlist.all()

    return render(request, "auctions/watchlist.html", {
        "watchlist": watchlist
    })

@login_required(login_url='login')
def create_listing(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            form = CreateListingForm(request.POST, request.FILES)            

            if form.is_valid():
                name = form.cleaned_data["name"]
                category = form.cleaned_data["category"]
                image = form.cleaned_data["image"]
                description = form.cleaned_data["description"]
                start_price = form.cleaned_data["start_price"]

                listing = Listing(
                    name = name,
                    category = Category.objects.get(category=category),
                    image = image,
                    lister=request.user,
                    description = description,
                    start_price = start_price,
                    is_active = True
                )
                listing.save()
                return HttpResponseRedirect(reverse("index"))

    return render(request, "auctions/create-listing.html", {
        "create_form": CreateListingForm()
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

            if request.POST["next"]:
                return HttpResponseRedirect(request.POST["next"])
            else:
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