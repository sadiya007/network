from django.urls import path

from . import views

app_name = "network"

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("post", views.post, name="post"),
    path("profile/<str:usernamestr>", views.profile, name="profile"),
    path("profile/<str:usernamestr>/<int:page>", views.profilePosts, name="profilePosts"),
    path("follow/<str:usernamestr>", views.follow, name="follow"),
    path("unfollow/<str:usernamestr>", views.unfollow, name="unfollow"),
    path("posts/<str:filter>/<int:page>", views.posts, name="posts"),
    path("like/<int:id>", views.like, name="like"),
    path("unlike/<int:id>", views.unlike, name="unlike"),
    path("editPost/<int:id>", views.editPost, name="editPost")
]