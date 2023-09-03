from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from user.models import Post, Profile, HashTag, Like
from user.serializers import PostListSerializer, PostLikeSerializer

POST_URL = reverse("user:post-list")


def detail_url(post_id):
    return reverse("user:post-detail", args=[post_id])


class UnauthenticatedProfileApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(POST_URL)
        self.assertEquals(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedProfileApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "testunique@tests.com", "unique_password"
        )
        self.user2 = get_user_model().objects.create_user(
            "test2unique@tests.com", "unique_password2"
        )
        self.client.force_authenticate(self.user)

    def test_post_list(self):
        post1 = Post.objects.create(
            user=self.user, title="testpost1", text="testpost1text"
        )
        post2 = Post.objects.create(
            user=self.user2, title="testpost2", text="testpost2text"
        )
        profile1 = Profile.objects.create(
            user=self.user, username="test1", bio="testbio1"
        )
        profile2 = Profile.objects.create(
            user=self.user2, username="test2", bio="testbio2"
        )
        profile1.following.add(self.user2)
        posts = Post.objects.all()
        res = self.client.get(POST_URL)
        serializer = PostListSerializer(posts, many=True)

        self.assertEquals(res.status_code, status.HTTP_200_OK)
        for key in serializer.data[0]:
            self.assertEquals(serializer.data[0][key], res.data["results"][0][key])

    def test_post_create(self):
        hashtag = HashTag.objects.create(name="testhash")
        payload = {
            "user": self.user,
            "title": "testtitle",
            "text": "testetext",
            "hashtag": [
                hashtag.id,
            ],
        }
        res = self.client.post(POST_URL, payload)
        print(res.data)
        self.assertEquals(res.status_code, status.HTTP_201_CREATED)

    def test_post_like(self):
        profile1 = Profile.objects.create(
            user=self.user, username="test1", bio="testbio1"
        )
        profile2 = Profile.objects.create(
            user=self.user2, username="test2", bio="testbio2"
        )
        profile1.following.add(self.user2)
        post2 = Post.objects.create(
            user=self.user2, title="testpost2", text="testpost2text"
        )
        post2_url = detail_url(post2.id)
        like_post_url = post2_url + "post_like_unlike/"
        res = self.client.post(like_post_url)
        posts = Post.objects.all()
        serializer = PostLikeSerializer(posts, many=True)

        self.assertEquals(res.status_code, status.HTTP_200_OK)
        self.assertEquals(res.data, serializer.data[0])

    def test_post_unlike(self):
        profile1 = Profile.objects.create(
            user=self.user, username="test1", bio="testbio1"
        )
        profile2 = Profile.objects.create(
            user=self.user2, username="test2", bio="testbio2"
        )
        profile1.following.add(self.user2)
        post2 = Post.objects.create(
            user=self.user2, title="testpost2", text="testpost2text"
        )
        post2_url = detail_url(post2.id)
        like_post_url = post2_url + "post_like_unlike/"
        res = self.client.post(like_post_url)
        res2 = self.client.post(like_post_url)

        self.assertEquals(res2.status_code, status.HTTP_200_OK)
        self.assertEquals(res2.data, {"status": "unliked"})

    def test_delete_own_post_allowed(self):
        profile1 = Profile.objects.create(
            user=self.user, username="test1", bio="testbio1"
        )
        post1 = Post.objects.create(
            user=self.user, title="testpost1", text="testpost1text"
        )

        post_url = detail_url(post1.id)
        res = self.client.delete(post_url)

        self.assertEquals(res.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_not_owners_post_not_allowed(self):
        profile1 = Profile.objects.create(
            user=self.user, username="test1", bio="testbio1"
        )
        profile2 = Profile.objects.create(
            user=self.user2, username="test2", bio="testbio2"
        )
        profile1.following.add(self.user2)
        post2 = Post.objects.create(
            user=self.user2, title="testpost2", text="testpost2text"
        )

        post_url = detail_url(post2.id)
        res = self.client.delete(post_url)

        self.assertEquals(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminProfileApiTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@admin.com", "admin1234", is_staff=True
        )
        self.user2 = get_user_model().objects.create_user(
            "test2unique@tests.com", "unique_password2"
        )
        self.client.force_authenticate(self.user)

    def test_delete_post_allowed(self):
        profile1 = Profile.objects.create(
            user=self.user, username="test1", bio="testbio1"
        )
        profile2 = Profile.objects.create(
            user=self.user2, username="test2", bio="testbio2"
        )
        profile1.following.add(self.user2)
        post2 = Post.objects.create(
            user=self.user2, title="testpost2", text="testpost2text"
        )
        url = detail_url(post2.id)

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
