from django.urls import path, include

from user.views import (
    CreateUserView,
    ProfileViewSet,
    HashTagViewSet,
    PostViewSet,
    CommentViewSet,
    LikedListPostsProfileOnlyView,
    LikedListCommentsProfileOnlyView,
)
from rest_framework import routers

router = routers.DefaultRouter()
router.register("profiles", ProfileViewSet)
router.register("hashtags", HashTagViewSet)
router.register("posts", PostViewSet)
router.register("comments", CommentViewSet)
router.register("likes-list-post", LikedListPostsProfileOnlyView)
router.register("likes-list-comment", LikedListCommentsProfileOnlyView)


urlpatterns = [
    path("", include(router.urls)),
    path("register_user/", CreateUserView.as_view(), name="create"),
]

app_name = "user"
