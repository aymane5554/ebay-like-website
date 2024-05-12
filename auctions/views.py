from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render , redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .models import User,Listing,Bid,Comment,Category
from django.core import exceptions

def index(request):
    listings = Listing.objects.filter(status="active").order_by("-date")
    return render(request, "auctions/index.html",{"listings":listings})


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

@login_required(login_url="/login")
def create(request):
    cat = Category.objects.all()
    if request.method == "POST" : 
        title = request.POST["t"]
        print(request.POST)
        description = request.POST["d"]
        price = request.POST["p"]
        image = request.FILES["i"]
        category = request.POST["category"]
        if category == "None" :
            category = None
        else : 
            category = Category.objects.get(pk = request.POST["category"])
        id = request.user.id
        user = User.objects.get(pk=id)
        s = Listing.objects.create(title=title,description=description,lister=user,price=price,image=image,category=category)
        s.save()
        return redirect("/")
    return render(request,"auctions/create.html",{"cats":cat})

def listing_view(request,id):
    listing = Listing.objects.get(pk=id)
    comments = Comment.objects.filter(listing=listing)
    if request.method == "POST":
        if "a" in request.POST :
            request.user.watchlist.add(listing)
            return redirect(f"/listing/{id}")
        elif "r" in request.POST :
            request.user.watchlist.remove(listing)
            return redirect(f"/listing/{id}")
        elif "b" in request.POST : 
            last_bid = listing.current_bid
            if last_bid == None :
                if float(request.POST["p"]) >= float(listing.price) :
                    b = Bid.objects.create(amount=float(request.POST["p"]),user=request.user,listing=listing)
                    listing.current_bid = b
                    listing.save()
                    return redirect(f"/listing/{id}")
                else : 
                    try :
                        w = request.user.watchlist.get(pk=id)
                    except exceptions.ObjectDoesNotExist :
                        w = None
                    else :w = request.user.watchlist.get(pk=id)
                    bids_num = Bid.objects.filter(listing=id).count()
                    return render(request,"auctions/listing.html",{"listing":listing,"w" :w,"msg":"The bid must be at least as large as the starting bid","bids":bids_num,"comments":comments})
            elif last_bid != None : 
                if float(request.POST["p"])  > listing.current_bid.amount :
                    b = Bid.objects.create(amount=float(request.POST["p"]),user=User.objects.get(pk=request.user.id),listing=listing)
                    listing.current_bid = b
                    listing.save()
                    return redirect(f"/listing/{id}")
                else :
                    try :
                        w = request.user.watchlist.get(pk=id)
                    except exceptions.ObjectDoesNotExist :
                        w = None
                    else :w = request.user.watchlist.get(pk=id)
                    bids_num = Bid.objects.filter(listing=id).count()
                    return render(request,"auctions/listing.html",{"listing":listing,"w" :w,"msg":"The bid must be larger than the last bid" ,"bids":bids_num,"comments":comments})
        elif "cmnt" in request.POST :
            comment = request.POST["cmnt"]
            if comment :
                Comment.objects.create(user=request.user,text=comment,listing=listing)
                return redirect(f"/listing/{id}")
        elif "close" in request.POST :
                listing.status = "closed"
                listing.save()
                return redirect(f"/listing/{id}")

    try :
        w = request.user.watchlist.get(pk=id)
    except exceptions.ObjectDoesNotExist :
        w = None
    else :w = request.user.watchlist.get(pk=id)
    bids_num = Bid.objects.filter(listing=id).count()
    return render(request,"auctions/listing.html",{"listing":listing,"w" :w,"bids":bids_num,"comments":comments})

def watchlist(request):
    listings = request.user.watchlist.all().order_by("-date")
    return render(request, "auctions/watchlist.html",{"listings":listings})

def categories(request):
    c = Category.objects.all()
    return render(request,"auctions/categories.html",{"categories":c})

def category_listings(request,category):
    if category == "others" : 
        l = Listing.objects.filter(category=None).order_by("-date")
        c = "Others"
        return render(request,"auctions/category.html",{"listings":l,"c" : c})
    c = Category.objects.get(name = category)
    l = Listing.objects.filter(category=c).order_by("-date")
    return render(request,"auctions/category.html",{"listings":l,"c" : c.name})