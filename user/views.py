from drf_spectacular.utils import extend_schema
from rest_framework import generics, viewsets, status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from user.models import Profile
from user.permissions import IsOwnerOrIsAdminOrReadOnly
from user.serializers import (
    UserSerializer,
    ProfileListSerializer,
    ProfileDetailSerializer,
    ProfileSerializer,
    ProfilePictureSerializer,
    FollowersProfileSerializer,
    FollowingProfileSerializer,
    AuthTokenSerializer,
)


class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)


class CreateTokenView(ObtainAuthToken):
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES
    serializer_class = AuthTokenSerializer


class ManageUserView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user


@extend_schema(description="Endpoint for logout user from the system")
class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            request.user.auth_token.delete()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    description="This endpoint gives user opportunity to manage own profile and view others"
)
class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = (IsOwnerOrIsAdminOrReadOnly, IsAuthenticated)

    def get_queryset(self):
        queryset = self.queryset

        """Filtering by username"""

        username = self.request.query_params.get("username")
        if username:
            queryset = queryset.filter(username__icontains=username)
        return (
            queryset.select_related("user")
            .prefetch_related("following", "followers")
            .distinct()
        )

    def get_serializer_class(self):
        if self.action == "list":
            return ProfileListSerializer
        if self.action == "retrieve":
            return ProfileDetailSerializer
        return ProfileSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(
        methods=["GET"],
        detail=False,
        url_path="my_profile",
        serializer_class=ProfileListSerializer,
    )
    def my_profile(self, request, pk=None):
        profile = self.request.user.profile
        serializer = self.serializer_class(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=["GET"],
        detail=True,
        url_path="profile_followers",
        serializer_class=FollowersProfileSerializer,
    )
    def profile_followers(self, request, pk=None):
        """Endpoint for list of profile followers"""
        profile = self.get_object()
        serializer = self.serializer_class(profile, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=["GET"],
        detail=True,
        url_path="profile_followings",
        serializer_class=FollowingProfileSerializer,
    )
    def profile_followings(self, request, pk=None):
        """Endpoint for list of profile followings"""
        profile = self.get_object()
        serializer = self.serializer_class(profile, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=["POST"],
        detail=True,
        url_path="follow_unfollow",
        permission_classes=[IsAuthenticated],
    )
    def follow_unfollow(self, request, pk=None):
        """Endpoint for following & unfollowing profile"""
        profile = self.get_object()
        user = self.request.user
        if user.profile and profile.id == user.profile.id:
            raise ValidationError("You cannot follow by yourself!!!")
        if profile.followers.filter(pk=user.pk).exists():
            profile.followers.remove(user)
            user.profile.following.remove(profile.user)
            return Response({"status": "unfollow"})
        profile.followers.add(user)
        user.profile.following.add(profile.user)
        return Response({"status": "follow"})

    @action(
        methods=["POST", "DELETE"],
        detail=True,
        url_path="upload-picture",
        serializer_class=ProfilePictureSerializer,
    )
    def upload_picture(self, request, pk=None):
        """Endpoint for uploading picture to specific profile"""
        profile = self.get_object()
        serializer = self.serializer_class(profile, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
