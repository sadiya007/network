from django.test import Client, TestCase
from .models import Post, User
from datetime import datetime
from django.utils import timezone
from .forms import PostForm
import json

def createUser(username, email, password):
    u = User()
    u.username = username
    u.email = email
    u.set_password(password)
    u.save()
    return u

# Create your tests here.
class TestsPostModel(TestCase):

    def test_get_post_message(self):
        """*** Printing the post needs to be equal to the post message ***"""
        u = createUser("foo", "foo@example.com", "exmaple")
        m = "New post message"
        p = Post()
        p.post(m, u)
        self.assertEqual(str(p), m)

    def test_get_post_user(self):
        """*** Post needs to be posted by a User ***"""
        u = createUser("foo", "foo@example.com", "exmaple")
        m = "New post message"
        p = Post()
        p.post(m, u)
        self.assertEqual(p.user, u)

    def test_get_post_timestamp(self):
        """*** Post needs to be timestamped ***"""
        u = createUser("foo", "foo@example.com", "exmaple")
        m = "New post message"
        p = Post()
        p.post(m, u)
        p.save()
        self.assertTrue(abs(p.created_at - timezone.now()) < timezone.timedelta(seconds=5))

    def test_model_post_serialize(self):
        """*** Should a post be created, then can be serialized ***"""
        u = createUser("foo", "foo@example.com", "example")
        m = "New post message 1"
        p = Post()
        p.post(m, u)
        self.assertJSONEqual("{\"id\": 1, \"message\": \"New post message 1\",\"user\": {\"username\": \"foo\"},\"likes\": 0, \"created_at\": \"" + datetime.now().strftime("%b %-d %Y, %-I:%M %p") + "\"}", p.serialize())

    def test_model_post_serialize_like_count(self):
        """*** Should foo like juan's post, then like count is serialized ***"""
        foo = createUser("foo", "foo@example.com", "example")
        juan = createUser("juan", "juan@example.com", "example")
        m = "New post message 1"
        p = Post()
        p.post(m, juan)
        foo.like(p)
        self.assertJSONEqual("{\"id\": 1, \"message\": \"New post message 1\",\"user\": {\"username\": \"juan\"},\"likes\": 1, \"created_at\": \"" + datetime.now().strftime("%b %-d %Y, %-I:%M %p") + "\"}", p.serialize())

    def test_like_count_2(self):
        """*** Should foo and juan liked zoe's post, then likeCount should return 2 ***"""
        foo = createUser("foo", "foo@example.com", "example")
        juan = createUser("juan", "juan@example.com", "example")
        zoe = createUser("zoe", "zoe@example.com", "example")
        p = Post()
        p.post("First post", zoe)
        foo.like(p)
        juan.like(p)
        self.assertEqual(p.likeCount(), 2)

class TestUserModel(TestCase):

    def test_follow(self):
        """*** Should foo follow juan, then juan followers must return foo ***"""
        foo = createUser("foo", "foo@example.com", "example")
        juan = createUser("juan", "juan@example.com", "example")
        foo.follow(juan)
        self.assertIn(foo, juan.followers.all())
        self.assertIn(juan, foo.following.all())
        self.assertNotIn(foo, juan.following.all())

    def test_like(self):
        """*** Should foo like juan's post, then liking objects contains that post ***"""
        foo = createUser("foo", "foo@example.com", "example")
        juan = createUser("juan", "juan@example.com", "example")
        m = "New post message 1"
        p = Post()
        p.post(m, juan)
        foo.like(p)
        self.assertIn(p, User.objects.get(username=foo.username).liking.all())

    def test_unlike(self):
        """*** Should foo unlike juan's post, then liking objects does not contains juan's post ***"""
        foo = createUser("foo", "foo@example.com", "example")
        juan = createUser("juan", "juan@example.com", "example")
        m = "New post message 1"
        p = Post()
        p.post(m, juan)
        foo.like(p)
        foo.unlike(p)
        self.assertNotIn(p, User.objects.get(username=foo.username).liking.all())

    def test_like_twice_unallowed(self):
        """*** Should foo like juan's post twice, then an exception is raised ***"""
        foo = createUser("foo", "foo@example.com", "example")
        juan = createUser("juan", "juan@example.com", "example")
        m = "New post message 1"
        p = Post()
        p.post(m, juan)
        foo.like(p)
        with self.assertRaises(Exception, ) as cm:
            foo.like(p)
        self.assertEqual(str(cm.exception), "Cannot like a post twice")

    def test_like_my_post_unallowed(self):
        """*** Should foo like his own post, then an exception is raised ***"""
        foo = createUser("foo", "foo@example.com", "example")
        m = "New post message 1"
        p = Post()
        p.post(m, foo)
        with self.assertRaises(Exception, ) as cm:
            foo.like(p)
        self.assertEqual(str(cm.exception), "Cannot like your own post")

    def test_unlike_not_found(self):
        """*** Should foo unlike an unexisting post, then an exception is raised ***"""
        foo = createUser("foo", "foo@example.com", "example")
        m = "New post message 1"
        p = Post()
        with self.assertRaises(Exception, ) as cm:
            foo.unlike(p)
        self.assertEqual(str(cm.exception), "You must like a post before liking it")

class TestIndexView(TestCase):

    def test_get_index_view(self):
        """*** Index view request needs to be with response 200 ***"""
        c = Client()
        response = c.get(f"/")
        self.assertEqual(response.status_code, 200)

class TestPostAction(TestCase):

    def test_post_action_return_302_logged_out(self):
        """*** Post action should return 302 on logged out request ***"""
        c = Client()
        response = c.post(f"/post")
        self.assertEqual(response.status_code, 302)
        response = c.get(f"/post")
        self.assertEqual(response.status_code, 302)

    def test_post_action_return_200(self):
        """*** Post action must return 200 ***"""
        u = createUser("foo", "foo@example.com", "example")
        c = Client()
        c.login(username='foo', password='example')
        response = c.post(f"/post")
        self.assertEqual(response.status_code, 200)

    def test_post_action_return_404_with_get_request(self):
        """*** Post action must return 404 error code on GET request ***"""
        u = createUser("foo", "foo@example.com", "example")
        c = Client()
        c.login(username='foo', password='example')
        response = c.get(f"/post")
        self.assertEqual(response.status_code, 404)

class TestLikeAction(TestCase):

    def test_like_action_return_200(self):
        """*** Should foo like juan's post, then response 200 should be returned ***"""
        foo = createUser("foo", "foo@example.com", "example")
        juan = createUser("juan", "juan@example.com", "example")
        m = "New post message 1"
        p = Post()
        p.post(m, juan)
        c = Client()
        c.login(username='foo', password='example')
        response = c.post(f"/like/1")
        self.assertEqual(response.status_code, 200)

    def test_like_return_404_with_put_request(self):
        """*** Like action must return 404 error code on PUT request ***"""
        foo = createUser("foo", "foo@example.com", "example")
        c = Client()
        c.login(username='foo', password='example')
        response = c.put(f"/like/1")
        self.assertEqual(response.status_code, 404)

    def test_like_action_return_302_logged_out(self):
        """*** Like action should return 302 on logged out request ***"""
        c = Client()
        response = c.post(f"/like/1")
        self.assertEqual(response.status_code, 302)

    def test_like_return_true_get_liked_post(self):
        """*** Should foo like juan's post, then response 200 should be returned, with true content ***"""
        foo = createUser("foo", "foo@example.com", "example")
        juan = createUser("juan", "juan@example.com", "example")
        m = "New post message 1"
        p = Post()
        p.post(m, juan)
        foo.like(p)
        c = Client()
        c.login(username='foo', password='example')
        response = c.get(f"/like/1")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertJSONEqual("{\"message\": \"true\"}", data)

    def test_like_return_false_get_not_liked_post(self):
        """*** Should foo not like juan's post, then response 200 should be returned, with true content ***"""
        foo = createUser("foo", "foo@example.com", "example")
        juan = createUser("juan", "juan@example.com", "example")
        m = "New post message 1"
        p = Post()
        p.post(m, juan)
        c = Client()
        c.login(username='foo', password='example')
        response = c.get(f"/like/1")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertJSONEqual("{\"message\": \"false\"}", data)

class TestUnlikeAction(TestCase):

    def test_unlike_action_return_200(self):
        """*** Should foo unlike juan's post, then response 200 should be returned ***"""
        foo = createUser("foo", "foo@example.com", "example")
        juan = createUser("juan", "juan@example.com", "example")
        m = "New post message 1"
        p = Post()
        p.post(m, juan)
        foo.like(p)
        c = Client()
        c.login(username='foo', password='example')
        response = c.post(f"/unlike/1")
        self.assertEqual(response.status_code, 200)

    def test_unlike_return_404_with_get_request(self):
        """*** Unlike action must return 404 error code on GET request ***"""
        foo = createUser("foo", "foo@example.com", "example")
        c = Client()
        c.login(username='foo', password='example')
        response = c.get(f"/unlike/1")
        self.assertEqual(response.status_code, 404)

    def test_unlike_action_return_302_logged_out(self):
        """*** Unlike action should return 302 on logged out request ***"""
        c = Client()
        response = c.post(f"/unlike/1")
        self.assertEqual(response.status_code, 302)

class TestProfile(TestCase):

    def test_get_profile_view(self):
        """*** Profile view get request should return 200 on logged out and logged in request ***"""
        u = createUser("foo", "foo@example.com", "example")
        c = Client()
        response = c.get(f"/profile/foo")
        self.assertEqual(response.status_code, 200)
        c.login(username='foo', password='example')
        response = c.get(f"/profile/foo")
        self.assertEqual(response.status_code, 200)

    def test_get_profile_view_post_request_not_available(self):
        """*** Profile view get request should return 404 on post request ***"""
        c = Client()
        response = c.post(f"/profile/foo")
        self.assertEqual(response.status_code, 404)

    def test_get_profile_view_post_404_when_user_not_found(self):
        """*** Profile view get request should return 404 when user is not found ***"""
        c = Client()
        response = c.get(f"/profile/foo")
        self.assertEqual(response.status_code, 404)

    def test_get_profile_view_return_profile_html(self):
        """*** Profile view get request should return network/profile.html ***"""
        foo = createUser("foo", "foo@example.com", "example")
        c = Client()
        response = c.get(f"/profile/foo")
        self.assertTemplateUsed(response, 'network/profile.html')

    def test_get_profile_view_context_data(self):
        """*** Profile view get request context should return user followed and following count ***"""
        foo = createUser("foo", "foo@example.com", "example")
        juan  = createUser("juan", "juan@example.com", "example")
        zoe = createUser("zoe", "zoe@example.com", "example")
        foo.follow(juan)
        foo.follow(zoe)
        zoe.follow(foo)
        c = Client()
        response = c.get(f"/profile/foo")
        self.assertEqual(response.context["followingCount"], 2)
        self.assertEqual(response.context["followersCount"], 1)

    def test_get_profile_view_context_data(self):
        """*** Profile view get request context should return username ***"""
        foo = createUser("foo", "foo@example.com", "example")
        c = Client()
        response = c.get(f"/profile/foo")
        self.assertEqual(response.context["usernamestr"], "foo")

    def test_get_profile_view_context_data(self):
        """*** Profile view get request context should return following flag true if user is followed ***"""
        foo = createUser("foo", "foo@example.com", "example")
        juan  = createUser("juan", "juan@example.com", "example")
        zoe = createUser("zoe", "zoe@example.com", "example")
        foo.follow(juan)
        foo.follow(zoe)
        zoe.follow(foo)
        c = Client()
        c.login(username='foo', password='example')
        response = c.get(f"/profile/zoe")
        self.assertTrue(response.context["following"])
        c.logout()
        c.login(username='zoe', password='example')
        response = c.get(f"/profile/juan")
        self.assertFalse(response.context["following"])

class TestFollow(TestCase):

    def test_follow_ok(self):
        """*** Should a user follow another user, return response 200 on posting follow/<str:usernamestr> ***"""
        foo = createUser("foo", "foo@example.com", "example")
        juan  = createUser("juan", "juan@example.com", "example")
        c = Client()
        c.login(username='foo', password='example')
        response = c.post(f"/follow/juan")
        self.assertEqual(response.status_code, 200)

    def test_follow_dont_allow_get_request(self):
        """*** Should a user follow another user via GET or PUT, return 404 response ***"""
        foo = createUser("foo", "foo@example.com", "example")
        juan  = createUser("juan", "juan@example.com", "example")
        c = Client()
        c.login(username='foo', password='example')
        response = c.get(f"/follow/juan")
        self.assertEqual(response.status_code, 404)
        response = c.put(f"/follow/juan")
        self.assertEqual(response.status_code, 404)

    def test_follow_return_302_logged_out(self):
        """*** Follow action should return 302 on logged out request ***"""
        foo = createUser("foo", "foo@example.com", "example")
        juan  = createUser("juan", "juan@example.com", "example")
        c = Client()
        response = c.post(f"/follow/juan")
        self.assertEqual(response.status_code, 302)

    def test_follow_return_404_when_user_not_found(self):
        """*** Follow request should return 404 when user is not found ***"""
        foo = createUser("foo", "foo@example.com", "example")
        juan  = createUser("juan", "juan@example.com", "example")
        c = Client()
        c.login(username='foo', password='example')
        response = c.post(f"/follow/zoe")
        self.assertEqual(response.status_code, 404)

    def test_follow_cant_follow_myself(self):
        """*** Should I follow myself, then return 404 ***"""
        foo = createUser("foo", "foo@example.com", "example")
        c = Client()
        c.login(username='foo', password='example')
        response = c.post(f"/follow/foo")
        self.assertEqual(response.status_code, 404)

    def test_follow_cant_follow_again(self):
        """*** Should I follow a user that I am already following, then return 404 ***"""
        foo = createUser("foo", "foo@example.com", "example")
        juan  = createUser("juan", "juan@example.com", "example")
        c = Client()
        c.login(username='foo', password='example')
        response = c.post(f"/follow/juan")
        response = c.post(f"/follow/juan")
        self.assertEqual(response.status_code, 404)

class TestUnfollow(TestCase):

    def test_follow_ok(self):
        """*** Should a user unfollow another user, return response 200 on posting unfollow/<str:usernamestr> ***"""
        foo = createUser("foo", "foo@example.com", "example")
        juan  = createUser("juan", "juan@example.com", "example")
        foo.follow(juan)
        c = Client()
        c.login(username='foo', password='example')
        response = c.post(f"/unfollow/juan")
        self.assertEqual(response.status_code, 200)

    def test_unfollow_allow_only_post_request(self):
        """*** Should a user unfollow another user via GET or PUT, return 404 response ***"""
        foo = createUser("foo", "foo@example.com", "example")
        juan  = createUser("juan", "juan@example.com", "example")
        foo.follow(juan)
        c = Client()
        c.login(username='foo', password='example')
        response = c.get(f"/unfollow/juan")
        self.assertEqual(response.status_code, 404)
        response = c.put(f"/unfollow/juan")
        self.assertEqual(response.status_code, 404)

    def test_unfollow_return_302_logged_out(self):
        """*** Unfollow action should return 302 on logged out request ***"""
        foo = createUser("foo", "foo@example.com", "example")
        juan  = createUser("juan", "juan@example.com", "example")
        foo.follow(juan)
        c = Client()
        response = c.post(f"/unfollow/juan")
        self.assertEqual(response.status_code, 302)

    def test_unfollow_cant_unfollow_myself(self):
        """*** Should I unfollow myself, then return 404 ***"""
        foo = createUser("foo", "foo@example.com", "example")
        c = Client()
        c.login(username='foo', password='example')
        response = c.post(f"/unfollow/foo")
        self.assertEqual(response.status_code, 404)

    def test_unfollow_return_404_when_user_not_found(self):
        """*** Unfollow request should return 404 when user is not found ***"""
        foo = createUser("foo", "foo@example.com", "example")
        juan  = createUser("juan", "juan@example.com", "example")
        foo.follow(juan)
        c = Client()
        c.login(username='foo', password='example')
        response = c.post(f"/unfollow/zoe")
        self.assertEqual(response.status_code, 404)

    def test_unfollow_cant_unfollow_again(self):
        """*** Should I unfollow a user that I am not already following, then return 404 ***"""
        foo = createUser("foo", "foo@example.com", "example")
        juan  = createUser("juan", "juan@example.com", "example")
        foo.follow(juan)
        c = Client()
        c.login(username='foo', password='example')
        response = c.post(f"/unfollow/juan")
        response = c.post(f"/unfollow/juan")
        self.assertEqual(response.status_code, 404)

class TestPostsRequest(TestCase):

    allowedFilters = ["all", "following"]

    def test_posts_filter_all_return_200(self):
        """*** Should I GET /posts/all/1, return 200 ***"""
        c = Client()
        response = c.get(f"/posts/all/1")
        self.assertEqual(response.status_code, 200)

    def test_posts_filter_all_return_404_on_post_request(self):
        """*** Should I POST /posts/all, then return 404 ***"""
        c = Client()
        response = c.post(f"/posts/all")
        self.assertEqual(response.status_code, 404)

    def test_posts_filter_following_logged_in_return_200(self):
        """*** Should I GET /posts/following/1 when logged in, return 200 ***"""
        u = createUser("foo", "foo@example.com", "example")
        c = Client()
        c.login(username='foo', password='example')
        response = c.get(f"/posts/following/1")
        self.assertEqual(response.status_code, 200)

    def test_posts_filter_all_return_all_posts(self):
        """*** Should I GET /posts/all/1, then return all posts ***"""
        u = createUser("foo", "foo@example.com", "example")
        m = "New post message 1"
        p = Post()
        p.post(m, u)
        m = "New post message 2"
        p = Post()
        p.post(m, u)
        c = Client()
        response = c.get(f"/posts/all/1")
        data = json.loads(response.content)
        self.assertEqual(len(data), 2)

    def test_posts_filter_following_return_404_on_logged_out_request(self):
        """*** Should I GET /posts/following when logged out, then return 404 ***"""
        c = Client()
        response = c.get(f"/posts/following")
        self.assertEqual(response.status_code, 404)

    def test_posts_filter_following_return_404_on_unrecognized_filter(self):
        """*** Should I GET /posts/unrecognized, then return 404 ***"""
        c = Client()
        response = c.get(f"/posts/unrecognized")
        self.assertEqual(response.status_code, 404)

    def test_posts_filter_following(self):
        """*** Should foo follow juan, then /posts/following/1 should return juan's posts in reverse order ***"""
        foo = createUser("foo", "foo@example.com", "example")
        juan  = createUser("juan", "juan@example.com", "example")
        foo.follow(juan)
        m1 = "New post message 1"
        p = Post()
        p.post(m1, juan)
        m2 = "New post message 2"
        p = Post()
        p.post(m2, juan)
        c = Client()
        c.login(username='foo', password='example')
        response = c.get(f"/posts/following/1")
        data = json.loads(response.content)
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]["message"], m2)
        self.assertEqual(data[1]["message"], m1)

    def test_posts_filter_not_following(self):
        """*** Should foo follow juan but not zoe, then /posts/following should return only juan's posts in reverse order ***"""
        foo = createUser("foo", "foo@example.com", "example")
        juan  = createUser("juan", "juan@example.com", "example")
        zoe = createUser("zoe", "zoe@example.com", "example")
        foo.follow(juan)
        m1 = "New post message 1"
        p = Post()
        p.post(m1, juan)
        m2 = "New post message 2"
        p = Post()
        p.post(m2, juan)
        m3 = "New post message 3"
        p = Post()
        p.post(m3, zoe)
        c = Client()
        c.login(username='foo', password='example')
        response = c.get(f"/posts/following/1")
        data = json.loads(response.content)
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]["message"], m2)
        self.assertEqual(data[1]["message"], m1)
        self.assertEqual(data[0]["user"]["username"], "juan")
        self.assertEqual(data[1]["user"]["username"], "juan")

    def test_posts_request_page_1_with_10_posts(self):
        """*** Should foo post 7 posts and juan post 8 posts, then first page request with all filter should return 10 posts ***"""
        foo = createUser("foo", "foo@example.com", "example")
        juan  = createUser("juan", "juan@example.com", "example")
        for i in range(1,8):
            m = f"New post message {i}"
            Post().post(m, foo)
        for i in range(8,16):
            m = f"New post message {i}"
            Post().post(m, juan)
        c = Client()
        response = c.get(f"/posts/all/1")
        data = json.loads(response.content)
        self.assertEqual(len(data), 10)

    def test_posts_request_page_2_with_5_posts(self):
        """*** Should foo post 7 posts and juan post 8 posts, then second page request with all filter should return 5 posts ***"""
        foo = createUser("foo", "foo@example.com", "example")
        juan  = createUser("juan", "juan@example.com", "example")
        for i in range(1,8):
            Post().post(f"New post message {i}", foo)
        for i in range(8,16):
            Post().post(f"New post message {i}", juan)
        c = Client()
        response = c.get(f"/posts/all/2")
        data = json.loads(response.content)
        self.assertEqual(len(data), 5)

if __name__ == "__main__":
    unittest.main()