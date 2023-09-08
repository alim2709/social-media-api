from rest_framework import serializers

from social_network.models import HashTag, Post, Comment, Like


class HashTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = HashTag
        fields = ("name",)


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ("id", "title", "text", "hashtag", "created_at")


class PostListSerializer(PostSerializer):
    user = serializers.StringRelatedField(many=False, read_only=True)
    hashtag = serializers.SlugRelatedField(many=True, read_only=True, slug_field="name")
    comments_count = serializers.IntegerField(read_only=True)
    likes_count = serializers.IntegerField(read_only=True)

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
    user = serializers.StringRelatedField(many=False, read_only=True)
    hashtag = serializers.SlugRelatedField(many=True, read_only=True, slug_field="name")
    comments = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field="text"
    )
    likes = serializers.StringRelatedField(many=True, read_only=True)

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
    likes = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Comment
        fields = ("id", "post", "text", "likes", "created_at")


class LikePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ("id", "user", "created_at")


class LikeCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ("id", "user", "created_at")


class PostLikeSerializer(serializers.ModelSerializer):
    likes = LikePostSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = ("likes",)


class CommentLikeSerializer(serializers.ModelSerializer):
    likes = LikeCommentSerializer(many=True, read_only=True)

    class Meta:
        model = Comment
        fields = ("likes",)


class CommentDetailSerializer(CommentSerializer):
    post = PostDetailSerializer(many=False, read_only=True)
    likes = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Comment
        fields = ("id", "post", "text", "likes", "created_at")


class LikeListPostSerializer(serializers.ModelSerializer):
    post = serializers.SlugRelatedField(many=False, read_only=True, slug_field="title")

    class Meta:
        model = Like
        fields = ("id", "post", "created_at")


class LikeListCommentSerializer(serializers.ModelSerializer):
    comment = serializers.SlugRelatedField(
        many=False, read_only=True, slug_field="text"
    )

    class Meta:
        model = Like
        fields = ("id", "comment", "created_at")
