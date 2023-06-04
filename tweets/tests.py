from django.conf import settings
from django.contrib.auth import SESSION_KEY, get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Tweet

User = get_user_model()


class TestHomeView(TestCase):
    def setUp(self):
        self.url = reverse("tweets:home")
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.client.force_login(self.user)
        Tweet.objects.create(user=self.user, content="test tweet")

    def test_success_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tweets/home.html")

        tweets = response.context["tweet_list"]
        self.assertQuerysetEqual(tweets, Tweet.objects.all())


class TestTweetCreateView(TestCase):
    def setUp(self):
        self.url = reverse("tweets:create")
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.client.force_login(self.user)

    def test_success_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tweets/create.html")

    def test_success_post(self):
        valid_data = {
            "content": "test content",
        }
        response = self.client.post(self.url, valid_data)

        self.assertRedirects(
            response,
            reverse(settings.LOGIN_REDIRECT_URL),
            status_code=302,
            target_status_code=200,
        )
        self.assertIn(SESSION_KEY, self.client.session)

    def test_failure_post_with_empty_content(self):
        empty_content_data = {"user": self.user, "content": ""}
        response = self.client.post(self.url, empty_content_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Tweet.objects.filter(**empty_content_data).exists())
        self.assertFalse(form.is_valid())
        self.assertIn("このフィールドは必須です。", form.errors["content"])

    def test_failure_post_with_too_long_content(self):
        long_content_data = {"content": "a" * 201}
        response = self.client.post(self.url, long_content_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Tweet.objects.filter(**long_content_data).exists())
        self.assertFalse(form.is_valid())
        self.assertIn("この値は 200 文字以下でなければなりません( 201 文字になっています)。", form.errors["content"])


class TestTweetDetailView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.client.force_login(self.user)
        self.tweet = Tweet.objects.create(user=self.user, content="test content")
        self.url = reverse("tweets:detail", kwargs={"pk": self.tweet.pk})

    def test_success_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tweets/detail.html")


class TestTweetDeleteView(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="testuser", password="testpassword")
        self.user2 = User.objects.create_user(username="testuser2", password="testpassword2")
        self.client.force_login(self.user1)
        self.tweet1 = Tweet.objects.create(user=self.user1, content="tweet1")
        self.tweet2 = Tweet.objects.create(user=self.user2, content="tweet2")
        self.url1 = reverse("tweets:delete", kwargs={"pk": self.tweet1.pk})
        self.url2 = reverse("tweets:delete", kwargs={"pk": self.tweet2.pk})

    def test_success_post(self):
        response = self.client.post(self.url1)
        self.assertRedirects(response, reverse("tweets:home"), status_code=302, target_status_code=200)
        self.assertEqual(Tweet.objects.count(), 1)

    def test_failure_post_with_not_exist_tweet(self):
        response = self.client.get(reverse("tweets:delete", kwargs={"pk": 100}))
        self.assertEqual(response.status_code, 404)
        self.assertEqual(Tweet.objects.count(), 2)

    def test_failure_post_with_incorrect_user(self):
        response = self.client.get(self.url2)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Tweet.objects.count(), 2)


# class TestLikeView(TestCase):
#     def test_success_post(self):

#     def test_failure_post_with_not_exist_tweet(self):

#     def test_failure_post_with_liked_tweet(self):


# class TestUnLikeView(TestCase):

#     def test_success_post(self):

#     def test_failure_post_with_not_exist_tweet(self):

#     def test_failure_post_with_unliked_tweet(self):
