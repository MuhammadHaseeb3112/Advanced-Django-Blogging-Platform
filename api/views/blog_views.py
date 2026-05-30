from django.core.cache import cache
from rest_framework.views import APIView
from django.db.models import Sum, Count
from rest_framework.decorators import action

from django.db.models import (
    Prefetch
)

from django_filters.rest_framework import (
    DjangoFilterBackend
)

from rest_framework import (

    filters,
    status,
    viewsets,

)


from rest_framework.permissions import (

    IsAuthenticated,
    IsAuthenticatedOrReadOnly,

)

from rest_framework.response import (
    Response
)

from blog.models import (

    BlogPost,
    Comment,
    Category,
    Tag,
    Notification,

)

from api.serializers.blog_serializers import (

    BlogListSerializer,
    BlogDetailSerializer,
    BlogCreateUpdateSerializer,
    CommentSerializer,
    CategorySerializer,
    TagSerializer,
    NotificationSerializer,
    AuthorSerializer,


)

from api.permissions.custom_permissions import (

    IsAuthorOrReadOnly,
    IsAdminOrAuthorRole,

)

from api.pagination.custom_pagination import (
    CustomPagination
)

from api.filters.blog_filters import (
    BlogPostFilter
)


from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from accounts.models import CustomUser




class AuthorProfileAPIView(APIView):

    permission_classes = [
        IsAuthenticatedOrReadOnly
    ]

    def get(self, request, username):

        try:

            author = CustomUser.objects.get(
                username=username
            )

        except CustomUser.DoesNotExist:

            return Response({

                "success": False,
                "message": "Author not found"

            }, status=404)

        posts = BlogPost.objects.filter(
            author=author,
            status='published'
        )

        serializer = BlogListSerializer(
            posts,
            many=True,
            context={
                'request': request
            }
        )

        return Response({

            "success": True,

            "author": AuthorSerializer(
                author
            ).data,

            "posts_count": posts.count(),

            "total_views": posts.aggregate(
                total=Sum('views')
            )['total'] or 0,

            "posts": serializer.data

        })


# =========================================
# BLOG POST VIEWSET
# =========================================

class BlogPostViewSet(
    viewsets.ModelViewSet
):


    pagination_class = CustomPagination

    filter_backends = [

        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,

    ]

    filterset_class = BlogPostFilter

    search_fields = [

        'title',
        'content',
        'short_description',

    ]

    ordering_fields = [

        'created_at',
        'views',
        'title',

    ]

    ordering = [

        '-created_at'

    ]


    lookup_field = "slug"
    lookup_url_kwarg = "slug"
    lookup_value_regex = r"[-a-zA-Z0-9_]+"

    # =====================================
    # DYNAMIC PERMISSIONS
    # =====================================

    def get_permissions(self):

        # CREATE / UPDATE / DELETE
        if self.action in [

            'create',
            'update',
            'partial_update',
            'destroy',

        ]:

            return [

                IsAuthenticated(),
                IsAdminOrAuthorRole(),
                IsAuthorOrReadOnly(),

            ]

        # READ ONLY
        return [

            IsAuthenticatedOrReadOnly()

        ]

    def get_queryset(self):

        return BlogPost.objects.select_related(

            'author',
            'category',

        ).prefetch_related(

            'tags',

            Prefetch(
                'comments',
                queryset=Comment.objects.select_related(
                    'author'
                )
            ),

            'likes',
            'bookmarks',

        ).all()

    # =====================================
    # DYNAMIC SERIALIZERS
    # =====================================

    def get_serializer_class(self):

        if self.action == 'list':

            return BlogListSerializer

        elif self.action in [

            'create',
            'update',
            'partial_update',

        ]:

            return BlogCreateUpdateSerializer

        return BlogDetailSerializer

    # =====================================
    # SAVE AUTHOR AUTOMATICALLY
    # =====================================

    def perform_create(self, serializer):

        cache.delete("trending_posts")

        serializer.save(
            author=self.request.user
    )

    def perform_update(self, serializer):

        cache.delete("trending_posts")

        serializer.save()
    
    def perform_destroy(self, instance):

        cache.delete("trending_posts")

        instance.delete()

    # =====================================
    # INCREASE VIEW COUNT
    # =====================================

    def retrieve(
        self,
        request,
        *args,
        **kwargs
    ):

        instance = self.get_object()

        instance.views += 1

        instance.save()

        serializer = self.get_serializer(
            instance
        )

        return Response(
            serializer.data
        )

    # =====================================
    # LIKE TOGGLE
    # =====================================

    @action(

        detail=True,

        methods=['post'],

        permission_classes=[IsAuthenticated]

    )

    def like(
        self,
        request,
        slug=None
    ):

        post = self.get_object()

        user = request.user

        if post.likes.filter(
            id=user.id
        ).exists():

            post.likes.remove(user)

            liked = False

            message = 'Post unliked'

        else:

            post.likes.add(user)

            liked = True

            message = 'Post liked'

        return Response({

            'success': True,
            'liked': liked,
            'likes_count': post.likes.count(),
            'message': message,

        })

    # =====================================
    # BOOKMARK TOGGLE
    # =====================================

    @action(

        detail=True,

        methods=['post'],

        permission_classes=[IsAuthenticated]

    )

    def bookmark(
        self,
        request,
        slug=None
    ):

        post = self.get_object()

        user = request.user

        if post.bookmarks.filter(
            id=user.id
        ).exists():

            post.bookmarks.remove(user)

            bookmarked = False

            message = 'Bookmark removed'

        else:

            post.bookmarks.add(user)

            bookmarked = True

            message = 'Post bookmarked'

        return Response({

            'success': True,
            'bookmarked': bookmarked,
            'bookmarks_count': (
                post.bookmarks.count()
            ),
            'message': message,

        })

    # =====================================
    # TRENDING POSTS
    # =====================================

    @action(
    detail=False,
    methods=['get']
)
    def trending(self, request):

        posts = BlogPost.objects.filter(
            status='published'
        ).order_by(
            '-views'
        )[:5]

        serializer = BlogListSerializer(
            posts,
            many=True,
            context={
            'request': request
            }
        )

        return Response({

            'success': True,
            'count': len(serializer.data),
            'results': serializer.data

        })



    @action(
    detail=False,
    methods=['get']
    )
    def most_viewed(self, request):

        cache_key = "most_viewed_posts"

        cached_data = cache.get(cache_key)

        if cached_data:
            return Response({
                "cached": True,
                "results": cached_data
            })

        posts = BlogPost.objects.filter(
            status="published"
        ).order_by("-views")[:10]

        serializer = BlogListSerializer(
            posts,
            many=True
        )

        data = serializer.data

        cache.set(
            cache_key,
            data,
            timeout=60 * 15
        )

        return Response({
            "cached": False,
            "results": data
        })


    @action(
        detail=False,
        methods=['get']
    )
    def recommended(self, request):

        posts = BlogPost.objects.filter(
        status='published'
).annotate(
        likes_count=Count('likes')
).order_by(
        '-likes_count',
        '-views'
)[:10]

        serializer = BlogListSerializer(
            posts,
            many=True
        )

        return Response(serializer.data)


    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated]
    )
    def my_stats(self, request):

        posts = BlogPost.objects.filter(
            author=request.user
        )

        return Response({

            "total_posts": posts.count(),

            "published_posts":
            posts.filter(
                status="published"
            ).count(),

            "draft_posts":
            posts.filter(
                status="draft"
            ).count(),

            "total_views":
            sum(
                post.views
                for post in posts
            ),

        })

    @action(
        detail=False,
        methods=['get']
    )
    def dashboard_analytics(self, request):

        data = cache.get(
            "dashboard_analytics"
        )

        if not data:

            return Response({

                "success": False,
                "message":
                "Analytics cache not available"

            })

        return Response({

            "success": True,
            "cached": True,
            "data": data

        })

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated]
    )
    def bookmarks(self, request):

        posts = BlogPost.objects.filter(
            bookmarks=request.user
        )

        serializer = BlogListSerializer(
            posts,
            many=True
        )

        return Response(serializer.data)


    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated]    
    )
    def liked_posts(self, request):

        posts = BlogPost.objects.filter(
            likes=request.user
        )

        serializer = BlogListSerializer(
            posts,
            many=True
        )

        return Response(serializer.data)
    


    @action(
    detail=False,
    methods=['get']
)
    def featured(self, request):

        posts = BlogPost.objects.filter(
        status='published'
    ).order_by('-views')[:5]

        serializer = BlogListSerializer(
        posts,
        many=True,
        context={'request': request}
    )

        return Response({
        "success": True,
        "count": len(serializer.data),
        "results": serializer.data
    })
    


    @action(
    detail=True,
    methods=['get'],
    url_path='related',
    url_name='related'
)
    def related(self, request, slug=None):

        post = self.get_object()

        posts = BlogPost.objects.filter(
            category=post.category,
            status='published'
        ).exclude(
            id=post.id
        )[:5]

        serializer = BlogListSerializer(
            posts,
            many=True,
            context={
                'request': request
            }
        )

        return Response({

            "success": True,
            "count": len(serializer.data),
            "results": serializer.data

        })


    

    def list(self, request, *args, **kwargs):

        cache_key = f"blogs_{request.get_full_path()}"

        cached_data = cache.get(cache_key)

        if cached_data:
            return Response(cached_data)

        response = super().list(
            request,
            *args,
            **kwargs
        )

        cache.set(
            cache_key,
            response.data,
            timeout=60 * 15
        )

        return response


# =========================================
# COMMENT VIEWSET
# =========================================

class CommentViewSet(
    viewsets.ModelViewSet
):

    serializer_class = CommentSerializer

    permission_classes = [

        IsAuthenticatedOrReadOnly,
        IsAuthorOrReadOnly,

    ]

    pagination_class = CustomPagination

    def get_queryset(self):

        return Comment.objects.select_related(

            'author',
            'post',

        ).all()

    def perform_create(self, serializer):

        print(serializer.validated_data)

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

    pagination_class = CustomPagination

    def get_permissions(self):

        if self.action in [

            'create',
            'update',
            'partial_update',
            'destroy',

        ]:

            return [

                IsAuthenticated(),
                IsAdminOrAuthorRole(),

            ]

        return [

            IsAuthenticatedOrReadOnly()

        ]

    def perform_create(self, serializer):

        cache.delete("categories")

        serializer.save()

    def perform_update(self, serializer):

        cache.delete("categories")

        serializer.save()

    def perform_destroy(self, instance):

        cache.delete("categories")

        instance.delete()



    def list(self, request, *args, **kwargs):

        cache_key = "categories"

        cached_data = cache.get(cache_key)

        if cached_data:
            return Response(cached_data)

        response = super().list(
            request,
            *args,
            **kwargs
        )

        cache.set(
            cache_key,
            response.data,
        timeout=60 * 60
        )

        return response


# =========================================
# TAG VIEWSET
# =========================================

class TagViewSet(
    viewsets.ModelViewSet
):

    queryset = Tag.objects.all()

    serializer_class = TagSerializer

    pagination_class = CustomPagination

    def get_permissions(self):

        if self.action in [

            'create',
            'update',
            'partial_update',
            'destroy',

        ]:

            return [

                IsAuthenticated(),
                IsAdminOrAuthorRole(),

            ]

        return [

            IsAuthenticatedOrReadOnly()

        ]
    

    def perform_create(self, serializer):

        cache.delete("tags")

        serializer.save()
    
    def perform_update(self, serializer):

        cache.delete("tags")

        serializer.save()

    def perform_destroy(self, instance):

        cache.delete("tags")

        instance.delete()



    def list(self, request, *args, **kwargs):

        cache_key = "tags"

        cached_data = cache.get(cache_key)

        if cached_data:
            return Response(cached_data)

        response = super().list(
            request,
            *args,
            **kwargs
        )

        cache.set(
            cache_key,
            response.data,
            timeout=60 * 60
        )

        return response

# =========================================
# NOTIFICATION VIEWSET
# =========================================

class NotificationViewSet(
    viewsets.ReadOnlyModelViewSet
):

    serializer_class = NotificationSerializer

    permission_classes = [
        IsAuthenticated
    ]

    pagination_class = CustomPagination

    def get_queryset(self):

        return Notification.objects.select_related(

            'sender',
            'post',

        ).filter(

            receiver=self.request.user

        ).order_by(

            '-created_at'

        )

    # =====================================
    # MARK AS READ
    # =====================================

    @action(

        detail=True,

        methods=['post']

    )

    def mark_as_read(
        self,
        request,
        pk=None
    ):

        notification = self.get_object()

        notification.is_read = True

        notification.save()

        return Response({

            'success': True,
            'message': 'Notification marked as read',

        })

    # =====================================
    # MARK ALL AS READ
    # =====================================

    @action(

        detail=False,

        methods=['post']

    )

    def mark_all_as_read(
        self,
        request
    ):

        self.get_queryset().update(
            is_read=True
        )

        return Response({

            'success': True,
            'message': (
                'All notifications marked as read'
            )

        })
    




