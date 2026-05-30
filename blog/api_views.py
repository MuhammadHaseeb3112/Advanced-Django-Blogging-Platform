from rest_framework import viewsets
from rest_framework import filters

from rest_framework.response import Response

from rest_framework.decorators import action

from rest_framework.permissions import (
    IsAuthenticated
)

from .models import (
    BlogPost,
    Comment,
    Category,
    Tag
)

from .serializers import (
    BlogPostSerializer,
    CommentSerializer,
    CategorySerializer,
    TagSerializer,
)

from .permissions import (
    IsAuthorOrReadOnly
)



# =========================================
# BLOG POST VIEWSET
# =========================================

class BlogPostViewSet(
    viewsets.ModelViewSet
):

    queryset = BlogPost.objects.all()

    serializer_class = BlogPostSerializer

    permission_classes = [

        IsAuthorOrReadOnly

    ]

    # =====================================
    # FILTERING
    # =====================================

    filterset_fields = [

        'status',

        'author',

        'category',

        'tags',

    ]

    # =====================================
    # SEARCH
    # =====================================

    search_fields = [

        'title',

        'content',

    ]

    # =====================================
    # ORDERING
    # =====================================

    ordering_fields = [

        'created_at',

        'title',

    ]

    def perform_create(self, serializer):

        serializer.save(
            author=self.request.user
        )

    # =====================================
    # LIKE TOGGLE API
    # =====================================

    @action(

        detail=True,

        methods=['post'],

        permission_classes=[IsAuthenticated]

    )

    def like(
        self,
        request,
        pk=None
    ):

        post = self.get_object()

        user = request.user

        if post.likes.filter(
            id=user.id
        ).exists():

            post.likes.remove(user)

            return Response(

                {
                    'message': 'Post unliked'
                }

            )

        else:

            post.likes.add(user)

            return Response(

                {
                    'message': 'Post liked'
                }

            )

    # =====================================
    # BOOKMARK TOGGLE API
    # =====================================

    @action(

        detail=True,

        methods=['post'],

        permission_classes=[IsAuthenticated]

    )

    def bookmark(
        self,
        request,
        pk=None
    ):

        post = self.get_object()

        user = request.user

        if post.bookmarks.filter(
            id=user.id
        ).exists():

            post.bookmarks.remove(user)

            return Response(

                {
                    'message': 'Bookmark removed'
                }

            )

        else:

            post.bookmarks.add(user)

            return Response(

                {
                    'message': 'Post bookmarked'
                }

            )


# =========================================
# COMMENT VIEWSET
# =========================================

class CommentViewSet(
    viewsets.ModelViewSet
):

    queryset = Comment.objects.all()

    serializer_class = CommentSerializer

    permission_classes = [

        IsAuthorOrReadOnly

    ]

    def perform_create(self, serializer):

        serializer.save(
            author=self.request.user
        )


# =========================================
# CATEGORY VIEWSET
# =========================================

class CategoryViewSet(
    viewsets.ModelViewSet
):

    queryset = Category.objects.all()

    serializer_class = CategorySerializer


# =========================================
# TAG VIEWSET
# =========================================

class TagViewSet(
    viewsets.ModelViewSet
):

    queryset = Tag.objects.all()

    serializer_class = TagSerializer


