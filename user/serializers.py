from django.contrib.auth import get_user_model
from rest_framework import serializers

from user.models import Profile, User, HashTag, Post


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
        fields = ("username", "bio")


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
        fields = ("title", "text", "hashtag", "created_at")


class PostListSerializer(PostSerializer):
    hashtag = serializers.SlugRelatedField(many=True, read_only=True, slug_field="name")

    class Meta:
        model = Post
        fields = ("user", "title", "text", "comments", "likes", "hashtag", "created_at")
