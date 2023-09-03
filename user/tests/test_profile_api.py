from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from user.models import Profile
from user.serializers import ProfileListSerializer

PROFILE_URL = reverse("user:profile-list")


def detail_url(profile_id):
    return reverse("user:profile-detail", args=[profile_id])


class UnauthenticatedProfileApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(PROFILE_URL)
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

    def test_list_profile(self):
        profile1 = Profile.objects.create(
            user=self.user, username="test1", bio="testbio1"
        )
        profile2 = Profile.objects.create(
            user=self.user2, username="test2", bio="testbio2"
        )

        profiles = Profile.objects.all()
        res = self.client.get(PROFILE_URL)

        serializer = ProfileListSerializer(profiles, many=True)

        self.assertEquals(res.status_code, status.HTTP_200_OK)
        self.assertEquals(res.data["results"], serializer.data)

    def test_follow_profile(self):
        profile1 = Profile.objects.create(
            user=self.user, username="test1", bio="testbio1"
        )
        profile2 = Profile.objects.create(
            user=self.user2, username="test2", bio="testbio2"
        )
        profile2_url = detail_url(profile2.id)
        follow_url = profile2_url + "follow_unfollow/"

        res = self.client.post(follow_url)
        self.assertEquals(res.status_code, status.HTTP_200_OK)
        self.assertEquals(res.data, {"status": "follow"})

    def test_unfollow_profile(self):
        profile1 = Profile.objects.create(
            user=self.user, username="test1", bio="testbio1"
        )
        profile2 = Profile.objects.create(
            user=self.user2, username="test2", bio="testbio2"
        )

        profile2.followers.add(self.user)
        profile2_url = detail_url(profile2.id)
        follow_url = profile2_url + "follow_unfollow/"
        res = self.client.post(follow_url)

        self.assertEquals(res.status_code, status.HTTP_200_OK)
        self.assertEquals(res.data, {"status": "unfollow"})

    def test_can_not_follow_own_profile(self):
        profile1 = Profile.objects.create(
            user=self.user, username="test1", bio="testbio1"
        )
        profile_url = detail_url(profile1.id)
        follow_url = profile_url + "follow_unfollow/"
        res = self.client.post(follow_url)
        self.assertEquals(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEquals(res.data[0], "You cannot follow by yourself!!!")

    def test_delete_own_profile_allowed(self):
        profile1 = Profile.objects.create(
            user=self.user, username="test1", bio="testbio1"
        )
        profile_url = detail_url(profile1.id)
        res = self.client.delete(profile_url)

        self.assertEquals(res.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_another_profile_not_allowed(self):
        profile1 = Profile.objects.create(
            user=self.user, username="test1", bio="testbio1"
        )
        profile2 = Profile.objects.create(
            user=self.user2, username="test2", bio="testbio2"
        )

        profile2_url = detail_url(profile2.id)

        res = self.client.delete(profile2_url)
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

    def test_delete_other_profiles(self) -> None:
        profile1 = Profile.objects.create(
            user=self.user, username="test1", bio="testbio1"
        )
        profile2 = Profile.objects.create(
            user=self.user2, username="test2", bio="testbio2"
        )
        url = detail_url(profile2.id)

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
