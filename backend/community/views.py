from django.shortcuts import render
from django.db.models import Count

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.response import Response

from .models import Post, Comment
from .serializers import PostListSerializer, PostDetailSerializer, CommentSerializer
from .permissions import IsOwnerOrReadOnly


class PostViewSet(viewsets.ModelViewSet):
    # 기본 queryset (최신순). list()에서 sort에 따라 다시 정렬함.
    queryset = Post.objects.all().order_by("-created_at")
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def get_serializer_class(self):
        if self.action == "list":
            return PostListSerializer
        return PostDetailSerializer

    # GET /api/community/posts/?sort=latest|oldest|likes
    def list(self, request, *args, **kwargs):
        sort = request.query_params.get("sort", "latest")

        qs = self.get_queryset()

        if sort == "oldest":
            qs = qs.order_by("created_at")
        elif sort == "likes":
            qs = qs.annotate(like_count=Count("likes")).order_by("-like_count", "-created_at")
        else:  # latest (기본)
            qs = qs.order_by("-created_at")

        serializer = self.get_serializer(qs, many=True, context={"request": request})

        return Response({
            "count": qs.count(),
            "results": serializer.data
        })

    # GET /api/community/posts/{id}/?sort=latest|oldest|likes  (댓글 정렬 기준)
    def retrieve(self, request, *args, **kwargs):
        post = self.get_object()
        sort = request.query_params.get("sort", "latest")

        comments = post.comments.all()

        if sort == "oldest":
            comments = comments.order_by("created_at")
        elif sort == "likes":
            comments = comments.annotate(
                like_count=Count("likes")
            ).order_by("-like_count", "-created_at")
        else:  # latest (기본)
            comments = comments.order_by("-created_at")

        serializer = self.get_serializer(
            post,
            context={
                "request": request,
                "sorted_comments": comments,
            }
        )
        return Response(serializer.data)

    # 로그인한 사용자 = 작성자
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    # POST /api/community/posts/{id}/like/
    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def like(self, request, pk=None):
        post = self.get_object()
        user = request.user

        if post.likes.filter(id=user.id).exists():
            post.likes.remove(user)
            liked = False
        else:
            post.likes.add(user)
            liked = True

        return Response({
            "liked": liked,
            "like_count": post.likes.count(),
        }, status=status.HTTP_200_OK)

    # 게시글에 댓글 작성
    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def comments(self, request, pk=None):
        post = self.get_object()

        serializer = CommentSerializer(
            data=request.data,
            context={"request": request}
        )
        serializer.is_valid(raise_exception=True)

        comment = serializer.save(
            post=post,
            author=request.user,
        )

        return Response(
            CommentSerializer(comment, context={"request": request}).data,
            status=status.HTTP_201_CREATED
        )


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all().order_by("-created_at")
    serializer_class = CommentSerializer

    # 로그인 필수, 작성자만 수정/삭제
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        return Comment.objects.all()

    def perform_update(self, serializer):
        serializer.save()

    def perform_destroy(self, instance):
        instance.delete()

    # POST /api/community/comments/{id}/like/
    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def like(self, request, pk=None):
        comment = self.get_object()
        user = request.user

        if comment.likes.filter(id=user.id).exists():
            comment.likes.remove(user)
            liked = False
        else:
            comment.likes.add(user)
            liked = True

        return Response({
            "liked": liked,
            "like_count": comment.likes.count(),
        }, status=status.HTTP_200_OK)
