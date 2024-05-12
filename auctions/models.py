from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    watchlist = models.ManyToManyField("Listing")

class Category(models.Model):
    name = models.CharField(max_length=64)

class Listing(models.Model):
    title = models.CharField(max_length=128)
    description = models.TextField()
    date = models.DateTimeField(auto_now_add = True)
    lister = models.ForeignKey(User,on_delete=models.CASCADE,related_name ="lister")
    current_bid = models.ForeignKey("Bid",on_delete=models.CASCADE,related_name="current_bid", default = None , null = True)
    price = models.FloatField()
    image = models.ImageField()
    status = models.CharField(max_length=16,default="active")
    category = models.ForeignKey(Category,on_delete=models.CASCADE,null=True)

class Bid(models.Model):
    amount = models.FloatField()
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name="bider")
    listing = models.ForeignKey(Listing,on_delete=models.CASCADE,related_name="listing")
    date = models.DateTimeField(auto_now_add = True)

class Comment(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name = "commenter")
    text = models.TextField()
    date = models.DateTimeField(auto_now_add = True)
    listing = models.ForeignKey(Listing,on_delete=models.CASCADE)
    
