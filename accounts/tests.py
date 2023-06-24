from django.conf import settings
from django.contrib.auth import SESSION_KEY, get_user_model
from django.test import TestCase
from django.urls import reverse

from tweets.models import Tweet

from .models import FriendShip

User = get_user_model()


class TestSignupView(TestCase):
    def setUp(self):
        self.url = reverse("accounts:signup")

    def test_success_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/signup.html")

    def test_success_post(self):
        valid_data = {
            "username": "testuser",
            "email": "test@test.com",
            "password1": "testpassword",
            "password2": "testpassword",
        }
        response = self.client.post(self.url, valid_data)

        self.assertRedirects(
            response,
            reverse(settings.LOGIN_REDIRECT_URL),
            status_code=302,
            target_status_code=200,
        )
        self.assertTrue(User.objects.filter(username=valid_data["username"]).exists())
        self.assertIn(SESSION_KEY, self.client.session)

    def test_failure_post_with_empty_form(self):
        empty_data = {
            "username": "",
            "email": "",
            "password1": "",
            "password2": "",
        }
        response = self.client.post(self.url, empty_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username=empty_data["username"]).exists())
        self.assertFalse(form.is_valid())
        self.assertIn("このフィールドは必須です。", form.errors["username"])
        self.assertIn("このフィールドは必須です。", form.errors["email"])
        self.assertIn("このフィールドは必須です。", form.errors["password1"])
        self.assertIn("このフィールドは必須です。", form.errors["password2"])

    def test_failure_post_with_empty_username(self):
        empty_username_data = {
            "username": "",
            "email": "test@test.com",
            "password1": "testpassword",
            "password2": "testpassword",
        }
        response = self.client.post(self.url, empty_username_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username=empty_username_data["username"]).exists())
        self.assertFalse(form.is_valid())
        self.assertIn("このフィールドは必須です。", form.errors["username"])

    def test_failure_post_with_empty_email(self):
        empty_email_data = {
            "username": "testuser",
            "email": "",
            "password1": "testpassword",
            "password2": "testpassword",
        }
        response = self.client.post(self.url, empty_email_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(email=empty_email_data["email"]).exists())
        self.assertFalse(form.is_valid())
        self.assertIn("このフィールドは必須です。", form.errors["email"])

    def test_failure_post_with_empty_password(self):
        empty_password_data = {
            "username": "testuser",
            "email": "test@test.com",
            "password1": "",
            "password2": "",
        }
        response = self.client.post(self.url, empty_password_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(password=empty_password_data["password1"]).exists())
        self.assertFalse(form.is_valid())
        self.assertIn("このフィールドは必須です。", form.errors["password1"])
        self.assertIn("このフィールドは必須です。", form.errors["password2"])

    def test_failure_post_with_duplicated_user(self):
        duplicated_user_data = {
            "username": "testuser",
            "email": "test@test.com",
            "password1": "testpassword",
            "password2": "testpassword",
        }

        User.objects.create_user(username="testuser", email="test2@test.com", password="testpassword")

        response = self.client.post(self.url, duplicated_user_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            User.objects.filter(
                username=duplicated_user_data["username"],
                email=duplicated_user_data["email"],
            ).exists()
        )
        self.assertFalse(form.is_valid())
        self.assertIn("同じユーザー名が既に登録済みです。", form.errors["username"])
        User.objects.last().delete()

    def test_failure_post_with_invalid_email(self):
        invalid_email_data = {
            "username": "testuser",
            "email": "test@test",
            "password1": "testpassword",
            "password2": "testpassword",
        }

        response = self.client.post(self.url, invalid_email_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(email=invalid_email_data["email"]).exists())
        self.assertFalse(form.is_valid())
        self.assertIn("有効なメールアドレスを入力してください。", form.errors["email"])

    def test_failure_post_with_too_short_password(self):
        short_password_data = {
            "username": "testuser",
            "email": "test@test.com",
            "password1": "djan",
            "password2": "djan",
        }

        response = self.client.post(self.url, short_password_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(password=short_password_data["password1"]).exists())
        self.assertFalse(form.is_valid())
        self.assertIn("このパスワードは短すぎます。最低 8 文字以上必要です。", form.errors["password2"])

    def test_failure_post_with_password_similar_to_username(self):
        similar_password_data = {
            "username": "testuser",
            "email": "test@test.com",
            "password1": "testusera",
            "password2": "testusera",
        }

        response = self.client.post(self.url, similar_password_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(password=similar_password_data["password1"]).exists())
        self.assertFalse(form.is_valid())
        self.assertIn("このパスワードは ユーザー名 と似すぎています。", form.errors["password2"])

    def test_failure_post_with_only_numbers_password(self):
        only_numbers_password_data = {
            "username": "testuser",
            "email": "test@test.com",
            "password1": "10293847",
            "password2": "10293847",
        }

        response = self.client.post(self.url, only_numbers_password_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(password=only_numbers_password_data["password1"]).exists())
        self.assertFalse(form.is_valid())
        self.assertIn("このパスワードは数字しか使われていません。", form.errors["password2"])

    def test_failure_post_with_mismatch_password(self):
        mismatch_password_data = {
            "username": "testuser",
            "email": "test@test.com",
            "password1": "testpassword",
            "password2": "differentpassword",
        }

        response = self.client.post(self.url, mismatch_password_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(password=mismatch_password_data["password1"]).exists())
        self.assertFalse(form.is_valid())
        self.assertIn("確認用パスワードが一致しません。", form.errors["password2"])


class TestLoginView(TestCase):
    def setUp(self):
        self.url = reverse("accounts:login")
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword",
        )

    def test_success_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/login.html")

    def test_success_post(self):
        valid_data = {
            "username": "testuser",
            "password": "testpassword",
        }
        response = self.client.post(self.url, valid_data)

        self.assertRedirects(
            response,
            reverse(settings.LOGIN_REDIRECT_URL),
            status_code=302,
            target_status_code=200,
        )
        self.assertIn(SESSION_KEY, self.client.session)

    def test_failure_post_with_not_exists_user(self):
        not_exists_data = {
            "username": "testuser2",
            "password": "testpassword",
        }
        response = self.client.post(self.url, not_exists_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertFalse(form.is_valid())
        self.assertNotIn(SESSION_KEY, self.client.session)
        self.assertIn("正しいユーザー名とパスワードを入力してください。どちらのフィールドも大文字と小文字は区別されます。", form.errors["__all__"])

    def test_failure_post_with_empty_password(self):
        empty_pass_data = {
            "username": "testuser",
            "password": "",
        }
        response = self.client.post(self.url, empty_pass_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertFalse(form.is_valid())
        self.assertNotIn(SESSION_KEY, self.client.session)
        self.assertIn("このフィールドは必須です。", form.errors["password"])


class TestLogoutView(TestCase):
    def setUp(self):
        self.url = reverse("accounts:logout")
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword",
        )
        self.client.force_login(self.user)

    def test_success_post(self):
        response = self.client.post(self.url)
        self.assertRedirects(
            response,
            reverse(settings.LOGOUT_REDIRECT_URL),
            status_code=302,
        )
        self.assertNotIn(SESSION_KEY, self.client.session)


class TestUserProfileView(TestCase):
    def setUp(self):
        self.login_user = User.objects.create_user(username="testuser", password="testpassword")
        self.target_user = User.objects.create_user(username="testuser2", password="testpassword2")
        self.client.force_login(self.login_user)
        self.target_tweet1 = Tweet.objects.create(user=self.target_user, content="tweet1")
        self.target_tweet2 = Tweet.objects.create(user=self.target_user, content="tweet2")
        self.own_tweet = Tweet.objects.create(user=self.login_user, content="tweet3")
        self.url = reverse("accounts:user_profile", kwargs={"username": self.target_user.username})

    def test_success_get(self):
        response = self.client.get(self.url)
        context = response.context

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/profile.html")
        self.assertQuerysetEqual(context["tweet_list"], Tweet.objects.filter(user=self.target_user), ordered=False)
        ct_follower = FriendShip.objects.filter(following__exact=self.target_user).count()
        self.assertEqual(context["followers_num"], ct_follower)
        ct_following = FriendShip.objects.filter(follower__exact=self.target_user).count()
        self.assertEqual(context["following_num"], ct_following)


class TestFollowView(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="test", password="password1")
        self.user2 = User.objects.create_user(username="test2", password="password2")
        self.client.force_login(self.user1)

    def test_success_post(self):
        url = reverse("accounts:follow", kwargs={"username": self.user2.username})
        response = self.client.post(url)
        self.assertRedirects(
            response,
            reverse("tweets:home"),
            status_code=302,
            target_status_code=200,
        )
        self.assertTrue(FriendShip.objects.filter(follower=self.user1, following=self.user2).exists())

    def test_failure_post_with_not_exist_user(self):
        url = reverse("accounts:follow", kwargs={"username": "not_exist_user"})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)
        self.assertFalse(FriendShip.objects.exists())

    def test_failure_post_with_self(self):
        url = reverse("accounts:follow", kwargs={"username": self.user1.username})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 400)
        self.assertFalse(FriendShip.objects.exists())


class TestUnfollowView(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="test", password="password1")
        self.user2 = User.objects.create_user(username="test2", password="password2")
        self.client.force_login(self.user1)
        FriendShip.objects.create(follower=self.user1, following=self.user2)

    def test_success_post(self):
        url = reverse("accounts:unfollow", kwargs={"username": self.user2.username})
        response = self.client.post(url)
        self.assertRedirects(
            response,
            reverse("tweets:home"),
            status_code=302,
            target_status_code=200,
        )
        self.assertFalse(FriendShip.objects.exists())

    def test_failure_post_with_not_exist_user(self):
        url = reverse("accounts:follow", kwargs={"username": "not_exist_user"})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)
        self.assertTrue(FriendShip.objects.filter(follower=self.user1, following=self.user2).exists())

    def test_failure_post_with_self(self):
        url = reverse("accounts:follow", kwargs={"username": self.user1.username})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 400)
        self.assertTrue(FriendShip.objects.filter(follower=self.user1, following=self.user2).exists())


class TestFollowingListView(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="test1", password="password1")
        self.user2 = User.objects.create_user(username="test2", password="password2")

        self.client.force_login(self.user1)
        FriendShip.objects.create(follower=self.user2, following=self.user1)
        self.url = reverse("accounts:following_list", kwargs={"username": self.user2.username})

    def test_success_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/following_list.html")
        self.assertEqual(response.context["following_list"].count(), 1)


class TestFollowerListView(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="test1", password="password1")
        self.user2 = User.objects.create_user(username="test2", password="password2")

        self.client.force_login(self.user1)
        FriendShip.objects.create(follower=self.user1, following=self.user2)
        self.url = reverse("accounts:follower_list", kwargs={"username": self.user2.username})

    def test_success_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/follower_list.html")
        self.assertEqual(response.context["follower_list"].count(), 1)
