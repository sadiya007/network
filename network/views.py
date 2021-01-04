from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.paginator import Paginator
import json

from .models import User, Post
from .forms import PostForm

itemsPerPage = 10

def index(request):
    # TODO: Pagination
    return render(request, "network/index.html", {
        "postForm": PostForm()
    });

def posts(request, filter, page):
    if request.method != "GET":
        raise Http404("Only GET requests allowed on this URL")
    if filter not in ["all", "following"]:
        raise Http404("Unrecognized filter")

    # filter: following
    if filter == "following":
        if not request.user.is_authenticated:
            raise Http404("Only logged in users allowed on this filter request")
        else:
            myUser = User.objects.get(username=request.user.username)
            usersFollowed = myUser.following.all()
            posts = Post.objects.filter(user__in=usersFollowed).order_by('-created_at')
            pages = Paginator(posts, itemsPerPage)
    # filter: all
    elif filter == "all":
        posts = Post.objects.all().order_by('-created_at')
        pages = Paginator(posts, itemsPerPage)

    # return filtered posts
    return JsonResponse([post.serialize() for post in pages.page(page)], safe=False)

def profilePosts(request, usernamestr, page):
    if request.method != "GET":
        raise Http404("Only GET requests allowed on this URL")

    try:
        u = User.objects.get(username=usernamestr)
        userPosts = u.usrPosts.all().order_by("-created_at")
        pages = Paginator(userPosts, itemsPerPage)
        # return filtered posts
        return JsonResponse([post.serialize() for post in pages.page(page)], safe=False)
    except Exception as e:
        raise Http404(f"Error while retrieving user data from {usernamestr}")

def profile(request, usernamestr):
    if request.method == "POST":
        raise Http404("Only GET requests allowed on this URL")

    following = False
    try:
        u = User.objects.get(username=usernamestr)
        followingCount = u.following.count()
        followersCount = u.followers.all().count()
        userPosts = u.usrPosts.all().order_by("-created_at")
        if request.user.is_authenticated:
            myUser = User.objects.get(username=request.user.username)
            following = (u in myUser.following.all())
    except Exception as e:
        raise Http404(f"Error while retrieving user data from {usernamestr}")

    return render(request, "network/profile.html", {
        "followingCount": followingCount,
        "followersCount": followersCount,
        "usernamestr": usernamestr,
        "following": following
    });

@login_required(login_url="network:login")
def follow(request, usernamestr):
    if request.method != "POST":
        raise Http404("Only POST requests allowed on this URL")
    if request.user.username == usernamestr:
        raise Http404("Recursive following not allowed")

    try:
        myUser = User.objects.get(username=request.user.username)
        u = User.objects.get(username=usernamestr)
        if u in myUser.following.all():
            raise Http404(f"Already following {usernamestr}")
        myUser.follow(u)
    except User.DoesNotExist:
        raise Http404(f"User {usernamestr} not found")
    return HttpResponse('OK')

@login_required(login_url="network:login")
def unfollow(request, usernamestr):
    if request.method != "POST":
        raise Http404("Only POST requests allowed on this URL")
    if request.user.username == usernamestr:
        raise Http404("Recursive following not allowed")

    try:
        myUser = User.objects.get(username=request.user.username)
        u = User.objects.get(username=usernamestr)
        if u not in myUser.following.all():
            raise Http404(f"You are not following {usernamestr}")
        myUser.unfollow(u)
    except User.DoesNotExist:
        raise Http404(f"User {usernamestr} not found")

    return HttpResponse('OK')

@login_required(login_url="network:login")
def like(request, id):
    if request.method not in ["GET","POST"]:
        raise Http404("Only POST requests allowed on this URL")
    if request.method == "POST":
        myUser = User.objects.get(username=request.user.username)
        post = Post.objects.get(pk=id)
        myUser.like(post)
        return HttpResponse('OK')
    if request.method == "GET":
        myUser = User.objects.get(username=request.user.username)
        post = Post.objects.get(pk=id)
        if post in myUser.liking.all():
            return JsonResponse({"message": "true"}, safe=False)
        else:
            return JsonResponse({"message": "false"}, safe=False)

@login_required(login_url="network:login")
def unlike(request, id):
    if request.method != "POST":
        raise Http404("Only POST requests allowed on this URL")

    myUser = User.objects.get(username=request.user.username)
    post = Post.objects.get(pk=id)
    myUser.unlike(post)
    return HttpResponse('OK')

@login_required(login_url="network:login")
def post(request):
    if request.method == "POST":
        f = PostForm(request.POST)
        if f.is_valid():
            newPost = f.save(commit=False)
            newPost.user = request.user
            newPost.save()
            f.save_m2m()
            return HttpResponseRedirect(reverse("network:index"))
        else:
            # TODO: Render error message
            return render(request, "network/index.html", {
                "postForm": PostForm()
            });
    else:
        raise Http404("Only POST request allowed on this URL")

@login_required(login_url="network:login")
def editPost(request, id):
    if request.method == "POST":
        post = Post.objects.get(pk=id)
        # Check if post edit request is from post owner
        if (post.user.username == request.user.username):
            data = json.loads(request.body)
            post.message = data.get("message")
            post.save()
            return JsonResponse(post.serialize(), status=201)
        else:
            return JsonResponse({"error": "Post edit not allowed"}, status=400)
    else:
        return JsonResponse({"error": "POST request required."}, status=400)

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("network:index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("network:index"))


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
        return HttpResponseRedirect(reverse("network:index"))
    else:
        return render(request, "network/register.html")