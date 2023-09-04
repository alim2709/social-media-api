from django.urls import path, include
from rest_framework import routers

from social_network.views import (
    HashTagViewSet,
    PostViewSet,
    CommentViewSet,
    LikedListPostsProfileOnlyView,
    LikedListCommentsProfileOnlyView,
)

router = routers.DefaultRouter()
router.register("hashtags", HashTagViewSet)
router.register("posts", PostViewSet)
router.register("comments", CommentViewSet)
router.register(
    "likes-list-post", LikedListPostsProfileOnlyView, basename="likes-list-post"
)
router.register(
    "likes-list-comment",
    LikedListCommentsProfileOnlyView,
    basename="likes-list-comment",
)

urlpatterns = [
    path("", include(router.urls)),
]

app_name = "social_network"
