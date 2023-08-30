from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

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
    path("register_user/", CreateUserView.as_view(), name="create"),
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
]

app_name = "user"
