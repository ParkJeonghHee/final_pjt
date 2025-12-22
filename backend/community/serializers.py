from rest_framework import serializers
from .models import Post, Comment


class CommentSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(
        source="author.username",
        read_only=True
    )
    like_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = [
            "id",
            "post",
            "content",
            "author",
            "author_username",
            "created_at",
            "updated_at",
            "like_count",
            "is_liked",
        ]
        read_only_fields = [
            "id",
            "post",
            "author",
            "author_username",
            "created_at",
            "updated_at",
            "like_count",
            "is_liked",
        ]

    def get_like_count(self, obj):
        return obj.likes.count()

    def get_is_liked(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return False
        return obj.likes.filter(id=request.user.id).exists()


class PostListSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(
        source="author.username",
        read_only=True
    )
    comment_count = serializers.SerializerMethodField()

    like_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            "id",
            "title",
            "author_username",
            "created_at",
            "updated_at",
            "comment_count",
            "like_count",
            "is_liked",  
        ]
        read_only_fields = [
            "id",
            "title",
            "author_username",
            "created_at",
            "updated_at",
            "comment_count",
            "like_count",
            "is_liked",
        ]

    def get_comment_count(self, obj):
        return obj.comments.count()

    def get_like_count(self, obj):
        return obj.likes.count()

    def get_is_liked(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return False
        return obj.likes.filter(id=request.user.id).exists()


class PostDetailSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(
        source="author.username",
        read_only=True
    )
    comments = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()

    like_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            "id",
            "title",
            "content",
            "author",
            "author_username",
            "created_at",
            "updated_at",
            "comment_count",
            "like_count",  
            "is_liked", 
            "comments",
        ]
        read_only_fields = [
            "id",
            "author",
            "author_username",
            "created_at",
            "updated_at",
            "comment_count",
            "like_count",
            "is_liked",
            "comments",
        ]

    def get_comment_count(self, obj):
        return obj.comments.count()

    def get_like_count(self, obj):
        return obj.likes.count()

    def get_is_liked(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return False
        return obj.likes.filter(id=request.user.id).exists()

    def get_comments(self, obj):
        comments = self.context.get("sorted_comments")
        if comments is None:
            comments = obj.comments.all()

        serializer = CommentSerializer(
            comments,
            many=True,
            context=self.context
        )
        return serializer.data
