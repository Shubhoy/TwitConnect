import json
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt

from .models import User, Post, Follow, Like


def index(request):
    post_like = []
    if request.user.is_authenticated:
        post_likes = Like.objects.filter(user=request.user)
        for use in post_likes:
            post_like.append(use.post)

    allpost = Post.objects.all().order_by('-date')
    paginator = Paginator(allpost, 5)
    page_number = request.GET.get('page')
    currentpage = paginator.get_page(page_number)
    return render(request, "network/index.html", {
        "allpost": allpost,
        "currentpage": currentpage,
        "post_like":post_like,
    })

@csrf_exempt
def like(request):
    if request.method == "POST":
        data = json.loads(request.body)
        post_id = data.get("post_id")
        post = Post.objects.get(pk = post_id)
        user_like = data.get("user_like")
        liked = Like(post = post, user = request.user)
        liked.save()
        return JsonResponse({"message": "Like"}, status=201)

@csrf_exempt
def dislike(request):
    if request.method == "POST":
        data = json.loads(request.body)
        post_id = data.get("post_id")
        post = Post.objects.get(pk = post_id)
        user_like = data.get("user_like")
        disliked = Like.objects.get(post = post, user = request.user)
        disliked.delete()
        return JsonResponse({"message": "Dislike"}, status=201)


def editing(request, post_id):
    if request.method == "GET":
        post = Post.objects.get(pk = post_id)
        return render(request,"network/editing.html",{
            "post":post,
        })
    else:
        content_edited = request.POST['content_edited'] 
        post = Post.objects.get(pk = post_id)
        post.content = content_edited
        post.save()
        return HttpResponseRedirect(reverse("index")) 

def follow(request, postuser_id):
     if request.method == "GET":
        user = request.user
        following = User.objects.get(pk=postuser_id)
        follow = Follow(user=user, following=following)
        follow.save()
        return HttpResponseRedirect(reverse("profile", args=(postuser_id,)))


def unfollow(request, postuser_id):
     if request.method == "GET":
        user = request.user
        following = User.objects.get(pk=postuser_id)
        record = Follow.objects.get(user=user, following=following)
        record.delete()
        return HttpResponseRedirect(reverse("profile", args=(postuser_id,)))


def profile(request, user_id):
    user = User.objects.get(pk=user_id)
    allpost = Post.objects.filter(user=user).order_by('-id')
    paginator = Paginator(allpost, 3)
    page_number = request.GET.get('page')
    currentpage = paginator.get_page(page_number)

    following = Follow.objects.filter(user=user)
    following_list = []
    follower_list = []
    for users in following:
        following_list.append(users.following)

    count_following = len(following)
    follower = Follow.objects.filter(following=user)
    count_follower = len(follower)
    for users in follower:
        follower_list.append(users.user)
    return render(request, "network/profile.html", {
        "profile_user": user,
        "following": following_list,
        "follower": follower_list,
        "currentpage": currentpage,
        "allpost": allpost,
        "count_following": count_following,
        "count_follower": count_follower,

    })


def newpost(request):
    if request.method == "POST":
        content = request.POST["content"]
        post = Post(content=content, user=request.user)
        post.save()
        return HttpResponseRedirect(reverse("index"))


def following(request):
    allpost= []
    following_user = []
    follow = Follow.objects.filter(user = request.user)
    for users in follow:
        following_user.append(users.following)
    
    for users in following_user:
        posts = Post.objects.filter(user = users)
        for post in posts:
            allpost.append(post)

    def returndate(e):
        return e.date
    allpost.sort(key=returndate, reverse=True)
    paginator = Paginator(allpost, 3)
    page_number = request.GET.get('page')
    currentpage = paginator.get_page(page_number)
    return render(request, "network/following.html", {
        "allpost": allpost,
        "currentpage": currentpage,
        "following" : following_user
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
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


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
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")
