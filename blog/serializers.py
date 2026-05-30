from rest_framework import serializers
from django.db.models import Avg

from .models import (
    BlogPost,
    Comment,
    Category,
    Tag

)



class CategorySerializer(
    serializers.ModelSerializer
):

    class Meta:

        model = Category

        fields = '__all__'

        ref_name = "WebsiteCategorySerializer"


class TagSerializer(
    serializers.ModelSerializer
):

    class Meta:

        model = Tag

        fields = '__all__'


        ref_name = "WebsiteTagSerializer"


# =========================================
# COMMENT SERIALIZER
# =========================================

class CommentSerializer(
    serializers.ModelSerializer
):

    author = serializers.StringRelatedField(
        read_only=True
    )

    class Meta:

        model = Comment

        fields = '__all__'

        ref_name = "WebsiteCommentSerializer"


# =========================================
# BLOG POST SERIALIZER
# =========================================

class BlogPostSerializer(
    serializers.ModelSerializer
):

    author = serializers.StringRelatedField(
        read_only=True
    )

    comments = CommentSerializer(
        many=True,
        read_only=True
    )

    category = CategorySerializer(
        read_only=True
    )


    tags = TagSerializer(
        many=True,
        read_only=True
    )

    average_rating = serializers.SerializerMethodField()

    likes_count = serializers.SerializerMethodField()

    is_liked = serializers.SerializerMethodField()

    bookmarks_count = serializers.SerializerMethodField()

    is_bookmarked = serializers.SerializerMethodField()



    class Meta:

        model = BlogPost

        fields = '__all__'

        ref_name = "WebsiteBlogPostSerializer"

    def get_average_rating(
        self,
        obj
    ):

        average = obj.comments.aggregate(
            Avg('rating')
        )['rating__avg']

        if average is None:

            return 0

        return round(average, 1)

    def validate_rating(self, value):

        if not 1 <= value <= 5:

            raise serializers.ValidationError(

            'Rating must be between 1 and 5'

        )

        return value
    
    def get_likes_count(
        self,
        obj
    ):

        return obj.likes.count()


    def get_is_liked(
        self,
        obj
    ):

        request = self.context.get('request')

        if request and request.user.is_authenticated:

            return obj.likes.filter(
                id=request.user.id
            ).exists()

        return False

    def get_bookmarks_count(
            self,
            obj
        ):

        return obj.bookmarks.count()


    def get_is_bookmarked(
        self,
        obj
    ):

        request = self.context.get('request')

        if request and request.user.is_authenticated:

            return obj.bookmarks.filter(
                id=request.user.id
            ).exists()

        return False
