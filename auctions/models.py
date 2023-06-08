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
    image = models.ImageField()
    lister = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")

    def highest_bid(self):
        highest_bid_instance = self.bid_set.order_by('-bid').first()
        if highest_bid_instance:
            return highest_bid_instance.bid
        return None
    
    def __str__(self):
        return f"{self.name}"

class Bid(models.Model):
    bidder = models.ForeignKey(User, on_delete=models.CASCADE)
    bid = models.DecimalField(decimal_places=2, max_digits=10)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.bid} by {self.bidder} on {self.listing}"