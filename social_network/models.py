from django.db import models

from social_media_api import settings


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
