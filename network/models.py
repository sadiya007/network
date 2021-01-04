from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    following = models.ManyToManyField('User', related_name="followers")
    liking = models.ManyToManyField('Post', related_name="likers")

    def follow(self, followed):
        self.following.add(followed)
        self.save()

    def unfollow(self, followed):
        self.following.remove(followed)
        self.save()

    def serialize(self):
        return {
            "username": self.username
        }

    def like(self, post):
        if self.username == post.user.username:
            raise Exception("Cannot like your own post")
        likes = self.liking.all()
        if post in likes:
            raise Exception("Cannot like a post twice")
        self.liking.add(post)
        self.save

    def unlike(self, post):
        likes = self.liking.all()
        if post not in likes:
            raise Exception("You must like a post before liking it")
        self.liking.remove(post)
        self.save

class Post(models.Model):
    message = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="usrPosts", default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    def post(self, message, user):
        self.message = message
        self.user = user
        self.save()

    def __str__(self):
        return self.message

    def serialize(self):
        return {
            "id": self.id,
            "message": self.message,
            "user": self.user.serialize(),
            "likes": self.likeCount(),
            "created_at": self.created_at.strftime("%b %-d %Y, %-I:%M %p")
        }

    def likeCount(self):
        return self.likers.all().count()