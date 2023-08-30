from django.contrib.auth import get_user_model
from rest_framework import serializers

from user.models import Profile, User, HashTag, Post, Comment, Like


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ["id", "email", "password", "is_staff", "profile"]
        read_only_fields = ["id", "is_staff", "profile"]
        extra_kwargs = {"password": {"write_only": True, "min_length": 8}}

    def create(self, validated_data):
        """Create user with encrypted password"""
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """Update user with correctly encrypted password"""
        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user


class FollowsSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("email",)
        list_serializer_class = serializers.ListSerializer

    def to_representation(self, instance):
        return instance.email


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ("id", "username", "bio")


class FollowersProfileSerializer(serializers.ModelSerializer):
    followers = FollowsSerializer(many=True, read_only=True)

    class Meta:
        model = Profile
        fields = ("followers",)


class FollowingProfileSerializer(serializers.ModelSerializer):
    following = FollowsSerializer(many=True, read_only=True)

    class Meta:
        model = Profile
        fields = ("following",)


class ProfilePictureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = (
            "id",
            "picture",
        )


class ProfileListSerializer(ProfileSerializer):
    followers = FollowsSerializer(many=True, read_only=True)
    following = FollowsSerializer(many=True, read_only=True)

    class Meta:
        model = Profile
        fields = ("id", "username", "picture", "bio", "followers", "following")
        read_only_fields = ("id", "picture")


class ProfileDetailSerializer(ProfileListSerializer):
    pass


class HashTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = HashTag
        fields = ("name",)


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ("id", "title", "text", "hashtag", "created_at")


class PostListSerializer(PostSerializer):
    hashtag = serializers.SlugRelatedField(many=True, read_only=True, slug_field="name")
    comments_count = serializers.IntegerField(source="number_of_comments")
    likes_count = serializers.IntegerField(source="num_likes")

    class Meta:
        model = Post
        fields = (
            "id",
            "user",
            "title",
            "text",
            "comments_count",
            "likes_count",
            "hashtag",
            "created_at",
        )


class PostDetailSerializer(PostSerializer):
    comments = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field="text"
    )

    class Meta:
        model = Post
        fields = (
            "id",
            "user",
            "title",
            "text",
            "comments",
            "likes",
            "hashtag",
            "created_at",
        )


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ("id", "post", "text", "created_at")


class CommentListSerializer(CommentSerializer):
    post = serializers.SlugRelatedField(many=False, read_only=True, slug_field="title")

    class Meta:
        model = Comment
        fields = ("id", "post", "text", "likes", "created_at")


class CommentDetailSerializer(CommentSerializer):
    post = PostDetailSerializer(many=False, read_only=True)


class LikePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ("id", "user", "created_at")


class LikeCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ("id", "comment", "created_at")


class PostLikeSerializer(serializers.ModelSerializer):
    likes = LikePostSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = ("likes",)
