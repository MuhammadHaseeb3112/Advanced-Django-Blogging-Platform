from django.db.models import Sum, Count

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import ListAPIView

from accounts.models import CustomUser

from blog.models import (
    BlogPost,
    Comment,
    Category,
    Tag,
)

from api.serializers.blog_serializers import (
    BlogListSerializer,
)


class DashboardAPIView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    def get(self, request):

        data = {

            "total_users":
                CustomUser.objects.count(),

            "total_posts":
                BlogPost.objects.count(),

            "total_comments":
                Comment.objects.count(),

            "total_categories":
                Category.objects.count(),

            "total_tags":
                Tag.objects.count(),

            "total_views":
                BlogPost.objects.aggregate(
                    total=Sum('views')
                )['total'] or 0,
        }

        return Response(data)
    



class MyPostsAPIView(ListAPIView):

    serializer_class = BlogListSerializer

    permission_classes = [IsAuthenticated]

    def get_queryset(self):

        return (
            BlogPost.objects
            .filter(author=self.request.user)
            .select_related(
                'author',
                'category'
            )
            .prefetch_related(
                'tags'
            )
        )
    
class DraftPostsAPIView(ListAPIView):

    serializer_class = BlogListSerializer

    permission_classes = [IsAuthenticated]

    def get_queryset(self):

        return (
            BlogPost.objects
            .filter(
                author=self.request.user,
                status='draft'
            )
            .select_related(
                'author',
                'category'
            )
            .prefetch_related(
                'tags'
            )
        )
    
class PublishedPostsAPIView(ListAPIView):

    serializer_class = BlogListSerializer

    permission_classes = [IsAuthenticated]

    def get_queryset(self):

        return (
            BlogPost.objects
            .filter(
                author=self.request.user,
                status='published'
            )
            .select_related(
                'author',
                'category'
            )
            .prefetch_related(
                'tags'
            )
        )
    


class BookmarkedPostsAPIView(ListAPIView):

    serializer_class = BlogListSerializer

    permission_classes = [
        IsAuthenticated
    ]

    def get_queryset(self):

        return BlogPost.objects.filter(
            bookmarks=self.request.user
        ).select_related(
            'author',
            'category'
        ).prefetch_related(
            'tags'
        )
    

class LikedPostsAPIView(ListAPIView):

    serializer_class = BlogListSerializer

    permission_classes = [
        IsAuthenticated
    ]

    def get_queryset(self):

        return BlogPost.objects.filter(
            likes=self.request.user
        ).select_related(
            'author',
            'category'
        ).prefetch_related(
            'tags'
        )
    


class AnalyticsAPIView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    def get(self, request):

        user_posts = BlogPost.objects.filter(
            author=request.user
        )

        data = {

            "total_posts":
                user_posts.count(),

            "published_posts":
                user_posts.filter(
                    status='published'
                ).count(),

            "draft_posts":
                user_posts.filter(
                    status='draft'
                ).count(),

            "total_views":
                user_posts.aggregate(
                    total=Sum('views')
                )['total'] or 0,

            "total_likes":
                sum(
                    post.likes.count()
                    for post in user_posts
                ),

            "total_comments":
                Comment.objects.filter(
                    post__author=request.user
                ).count(),

            "total_bookmarks":
                sum(
                    post.bookmarks.count()
                    for post in user_posts
                ),

        
        }

        return Response(data)