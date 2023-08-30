from django.db.models import Q
from rest_framework import generics, viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from user.models import Profile, HashTag, Post, Comment, Like
from user.serializers import (
    UserSerializer,
    ProfileListSerializer,
    ProfileDetailSerializer,
    ProfileSerializer,
    ProfilePictureSerializer,
    HashTagSerializer,
    PostSerializer,
    PostListSerializer,
    FollowersProfileSerializer,
    FollowingProfileSerializer,
    CommentSerializer,
    PostDetailSerializer,
    CommentListSerializer,
    CommentDetailSerializer,
    PostLikeSerializer,
    CommentLikeSerializer,
    LikeListPostSerializer,
    LikeListCommentSerializer,
)


class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer

    def get_queryset(self):
        queryset = self.queryset

        """Filtering by username"""

        username = self.request.query_params.get("username")
        if username:
            queryset = queryset.filter(username__icontains=username)
        return queryset.distinct()

    def get_serializer_class(self):
        if self.action == "list":
            return ProfileListSerializer
        if self.action == "retrieve":
            return ProfileDetailSerializer
        if self.action == "upload_picture":
            return ProfilePictureSerializer
        if self.action == "profile_followers":
            return FollowersProfileSerializer
        if self.action == "profile_followings":
            return FollowingProfileSerializer
        return ProfileSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(methods=["GET"], detail=True, url_path="profile_followers")
    def profile_followers(self, request, pk=None):
        """Endpoint for list of profile followers"""
        profile = self.get_object()
        serializer = self.get_serializer(profile, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=["GET"], detail=True, url_path="profile_followings")
    def profile_followings(self, request, pk=None):
        """Endpoint for list of profile followings"""
        profile = self.get_object()
        serializer = self.get_serializer(profile, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=["POST"],
        detail=True,
        url_path="follow_unfollow",
    )
    def follow_unfollow(self, request, pk=None):
        """Endpoint for following & unfollowing profile"""
        profile = self.get_object()
        user = self.request.user
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
    )
    def upload_picture(self, request, pk=None):
        """Endpoint for uploading picture to specific profile"""
        profile = self.get_object()
        serializer = self.get_serializer(profile, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class HashTagViewSet(viewsets.ModelViewSet):
    queryset = HashTag.objects.all()
    serializer_class = HashTagSerializer


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return PostListSerializer
        if self.action == "retrieve":
            return PostDetailSerializer
        if self.action == "post_like_unlike":
            return PostLikeSerializer
        return PostSerializer

    def get_queryset(self):
        queryset = self.queryset
        following_users = self.request.user.profile.following.all()
        queryset = queryset.filter(
            Q(user=self.request.user) | Q(user__in=list(following_users))
        )
        """Filtering posts by title & hashtags"""
        title = self.request.query_params.get("title")
        hashtag = self.request.query_params.get("hashtag")
        if title:
            queryset = queryset.filter(title__icontains=title)
        if hashtag:
            queryset = queryset.filter(hashtag__name__icontains=hashtag)
        return queryset.distinct()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(methods=["POST"], detail=True, url_path="post_like_unlike")
    def post_like_unlike(self, request, pk=None):
        """Endpoint for like/unlike posts"""
        post = self.get_object()
        user = self.request.user
        serializer = self.get_serializer(post, data=request.data)
        if not post.likes.filter(user=user).exists():
            Like.objects.create(user=user, post=post)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        post.likes.filter(user=user).delete()
        return Response({"status": "unliked"})


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def get_queryset(self):
        queryset = self.queryset
        following_users = self.request.user.profile.following.all()
        queryset = queryset.filter(
            Q(user=self.request.user) | Q(user__in=list(following_users))
        )
        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return CommentListSerializer
        if self.action == "retrieve":
            return CommentDetailSerializer
        if self.action == "comment_like_unlike":
            return CommentLikeSerializer
        return CommentSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(methods=["POST"], detail=True, url_path="comment_like_unlike")
    def comment_like_unlike(self, request, pk=None):
        """Endpoint for like/unlike comments"""
        comment = self.get_object()
        user = self.request.user
        serializer = self.get_serializer(comment, data=request.data)
        if not comment.likes.filter(user=user).exists():
            Like.objects.create(user=user, comment=comment)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        comment.likes.filter(user=user).delete()
        return Response({"status": "unliked comment"})


class LikedListPostsProfileOnlyView(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Like.objects.all()
    serializer_class = LikeListPostSerializer

    def get_queryset(self):
        queryset = self.queryset
        user = self.request.user
        queryset = queryset.filter(comment__isnull=True, user=user)
        return queryset


class LikedListCommentsProfileOnlyView(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Like.objects.all()
    serializer_class = LikeListCommentSerializer

    def get_queryset(self):
        queryset = self.queryset
        user = self.request.user
        queryset = queryset.filter(post__isnull=True, user=user)
        return queryset
