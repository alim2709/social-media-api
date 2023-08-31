import os
import uuid

from django.contrib.auth.models import (
    AbstractUser,
    BaseUserManager,
)  # A new class is imported. #
from django.db import models
from django.utils.translation import gettext as _
from django.utils.text import slugify

from social_media_api import settings


class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None
    email = models.EmailField(_("email address"), unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email


def profile_picture_file_path(instance, filename):
    _, extension = os.path.splitext(filename)
    filename = f"{slugify(instance.username)}-{uuid.uuid4()}.{extension}"
    return os.path.join("uploads/pictures/", filename)


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile"
    )
    username = models.CharField(max_length=255, unique=True)
    picture = models.ImageField(
        null=True, upload_to=profile_picture_file_path, blank=True
    )
    bio = models.TextField()
    followers = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="profiles_followers", blank=True
    )
    following = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="profiles_following", blank=True
    )

    class Meta:
        ordering = ("username",)

    def __str__(self):
        return self.username


class Like(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="likes",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    post = models.ForeignKey(
        "Post", on_delete=models.SET_NULL, null=True, related_name="likes"
    )
    comment = models.ForeignKey(
        "Comment", on_delete=models.SET_NULL, null=True, related_name="likes"
    )

    def __str__(self):
        return f"Liked at: {self.created_at} by {self.user}"


class Comment(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="comments"
    )
    post = models.ForeignKey(
        "Post", on_delete=models.CASCADE, null=True, related_name="comments"
    )
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment created at: {self.created_at}"


class HashTag(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Post(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="posts"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=60, unique=True)
    text = models.TextField()
    hashtag = models.ManyToManyField(HashTag, related_name="posts")

    def __str__(self):
        return self.title
