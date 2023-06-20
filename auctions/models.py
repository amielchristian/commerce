from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Category(models.Model):
    category = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.category}"

class Listing(models.Model):
    name = models.CharField(max_length=64)
    category = models.ForeignKey(Category, on_delete=models.RESTRICT)
    image = models.ImageField(upload_to="auctions/static/auctions")
    lister = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")
    description = models.TextField(null=True, blank=True, max_length=500)
    time = models.DateTimeField(auto_now_add=True)
    start_price = models.DecimalField(decimal_places=2, max_digits=10)
    is_active = models.BooleanField()

    def image_name(self):
        dir = self.image.name.split("/")
        return dir[-1]

    def highest_bid(self):
        highest_bid_instance = self.bids.order_by('-bid').first()
        if highest_bid_instance:
            return highest_bid_instance.bid
        return self.start_price
    
    def highest_bidder(self):
        highest_bid_instance = self.bids.order_by('-bid').first()
        if highest_bid_instance:
            return highest_bid_instance.bidder
        return "0"
    
    def __str__(self):
        return f"{self.name}"

class Bid(models.Model):
    bidder = models.ForeignKey(User, on_delete=models.CASCADE)
    bid = models.DecimalField(decimal_places=2, max_digits=10)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids")

    def __str__(self):
        return f"{self.bid} by {self.bidder} on {self.listing}"
    
class Comment(models.Model):
    comment = models.CharField(max_length=1000000000)
    commenter = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments")
    time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Regarding {self.listing}, {self.commenter} said {self.comment}"