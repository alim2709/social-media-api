from django.urls import path, include

from user.views import CreateUserView, ProfileViewSet, HashTagViewSet, PostViewSet
from rest_framework import routers

router = routers.DefaultRouter()
router.register("profiles", ProfileViewSet)
router.register("hashtags", HashTagViewSet)
router.register("posts", PostViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("register_user/", CreateUserView.as_view(), name="create"),
]

app_name = "user"
