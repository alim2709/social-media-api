from django.db.models import Q, Count
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from social_network.models import HashTag, Post, Like, Comment
from social_network.serializers import (
    HashTagSerializer,
    PostSerializer,
    PostListSerializer,
    PostDetailSerializer,
    PostLikeSerializer,
    CommentSerializer,
    CommentListSerializer,
    CommentDetailSerializer,
    CommentLikeSerializer,
    LikeListPostSerializer,
    LikeListCommentSerializer,
)
from user.permissions import IsOwnerOrIsAdminOrReadOnly, IsUserHaveProfile


@extend_schema(description="Endpoint for managing hashtags")
class HashTagViewSet(viewsets.ModelViewSet):
    queryset = HashTag.objects.all()
    serializer_class = HashTagSerializer
    permission_classes = (IsAuthenticated,)


@extend_schema(description="Endpoint for managing Posts")
class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (
        IsOwnerOrIsAdminOrReadOnly,
        IsAuthenticated,
        IsUserHaveProfile,
    )

    def get_serializer_class(self):
        if self.action == "list":
            return PostListSerializer
        if self.action == "retrieve":
            return PostDetailSerializer
        return PostSerializer

    def get_queryset(self):
        queryset = self.queryset

        following_users = self.request.user.profile.following.all()
        queryset = queryset.select_related("user__profile").filter(
            Q(user=self.request.user) | Q(user__in=following_users)
        )

        if self.action == "list":
            queryset = queryset.select_related("user").annotate(
                comments_count=Count("comments"), likes_count=Count("likes")
            )
        """Filtering posts by title & hashtags"""
        title = self.request.query_params.get("title")
        hashtag = self.request.query_params.get("hashtag")
        if title:
            queryset = queryset.filter(title__icontains=title)
        if hashtag:
            queryset = queryset.filter(hashtag__name__icontains=hashtag)
        return queryset.select_related("user").prefetch_related("hashtag").distinct()

    def get_permissions(self):
        if self.action == "post_like_unlike":
            return [IsAuthenticated()]
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(
        methods=["POST"],
        detail=True,
        url_path="post_like_unlike",
        serializer_class=PostLikeSerializer,
    )
    def post_like_unlike(self, request, pk=None):
        """Endpoint for like/unlike posts"""
        post = self.get_object()
        user = self.request.user

        if not post.likes.filter(user=user).exists():
            Like.objects.create(user=user, post=post)
            serializer = self.serializer_class(post)
            return Response(serializer.data, status=status.HTTP_200_OK)
        post.likes.filter(user=user).delete()
        return Response({"status": "unliked"})

    # Only for documentation purposes
    @extend_schema(
        parameters=[
            OpenApiParameter(
                "title",
                type={"type": "string"},
                description="Filter by source  (ex. ?title=ka)",
            ),
            OpenApiParameter(
                "hashtag",
                type={"type": "string"},
                description="Filter by hashtag  (ex. ?hashtag=pa)",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


@extend_schema(description="Endpoint for managing comments")
class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = (
        IsOwnerOrIsAdminOrReadOnly,
        IsAuthenticated,
        IsUserHaveProfile,
    )

    def get_queryset(self):
        queryset = self.queryset
        following_users = self.request.user.profile.following.all()
        queryset = queryset.filter(
            Q(user=self.request.user) | Q(user__in=following_users)
        )
        return queryset.select_related("post__user").prefetch_related(
            "likes__user",
        )

    def get_serializer_class(self):
        if self.action == "list":
            return CommentListSerializer
        if self.action == "retrieve":
            return CommentDetailSerializer
        return CommentSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(
        methods=["POST"],
        detail=True,
        url_path="comment_like_unlike",
        serializer_class=CommentLikeSerializer,
    )
    def comment_like_unlike(self, request, pk=None):
        """Endpoint for like/unlike comments"""
        comment = self.get_object()
        user = self.request.user

        if not comment.likes.filter(user=user).exists():
            Like.objects.create(user=user, comment=comment)
            serializer = self.serializer_class(comment)
            return Response({"status": "liked"}, status=status.HTTP_200_OK)
        comment.likes.filter(user=user).delete()
        return Response({"status": "unliked comment"})


@extend_schema(description="Endpoint for looking user's liked posts")
class LikedListPostsProfileOnlyView(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Like.objects.all()
    serializer_class = LikeListPostSerializer
    permission_classes = (IsOwnerOrIsAdminOrReadOnly, IsAuthenticated)

    def get_queryset(self):
        queryset = self.queryset
        user = self.request.user
        queryset = queryset.select_related("post__user").filter(
            comment__isnull=True, user=user
        )
        return queryset


@extend_schema(description="Endpoint for looking user's liked comments")
class LikedListCommentsProfileOnlyView(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Like.objects.all()
    serializer_class = LikeListCommentSerializer
    permission_classes = (IsOwnerOrIsAdminOrReadOnly, IsAuthenticated)

    def get_queryset(self):
        queryset = self.queryset
        user = self.request.user
        queryset = queryset.filter(post__isnull=True, user=user).select_related(
            "comment__post__user"
        )
        return queryset
