from rest_framework import serializers

from blog.models import (

    BlogPost,
    Comment,
    Category,
    Tag,
    Notification,

)

from accounts.models import CustomUser


# =========================================
# AUTHOR SERIALIZER
# =========================================

class AuthorSerializer(
    serializers.ModelSerializer
):

    class Meta:

        model = CustomUser

        fields = [

            'id',
            'username',
            'profile_image',

        ]


# =========================================
# CATEGORY SERIALIZER
# =========================================

class CategorySerializer(
    serializers.ModelSerializer
):

    class Meta:

        model = Category

        fields = [

            'id',
            'name',
            'slug',

        ]


# =========================================
# TAG SERIALIZER
# =========================================

class TagSerializer(
    serializers.ModelSerializer
):

    class Meta:

        model = Tag

        fields = [

            'id',
            'name',
            'slug',

        ]


# =========================================
# COMMENT SERIALIZER
# =========================================
class CommentSerializer(
    serializers.ModelSerializer
):

    post = serializers.PrimaryKeyRelatedField(
        queryset=BlogPost.objects.all()
    )

    author = AuthorSerializer(
        read_only=True
    )

    class Meta:

        model = Comment

        fields = [

            'id',
            'post',
            'author',
            'rating',
            'content',
            'created_at',

        ]

        read_only_fields = [

            'id',
            'author',
            'created_at',

        ]

# =========================================
# BLOG LIST SERIALIZER
# =========================================

class BlogListSerializer(
    serializers.ModelSerializer
):

    author = AuthorSerializer(
        read_only=True
    )

    category = CategorySerializer(
        read_only=True
    )

    likes_count = serializers.SerializerMethodField()

    comments_count = serializers.SerializerMethodField()

    average_rating = serializers.SerializerMethodField()

    class Meta:

        model = BlogPost

        fields = [

            'id',
            'title',
            'slug',
            'featured_image',
            'short_description',
            'author',
            'category',
            'status',
            'views',
            'likes_count',
            'comments_count',
            'average_rating',
            'created_at',

        ]

    def get_likes_count(self, obj):

        return obj.likes.count()

    def get_comments_count(self, obj):

        return obj.comments.count()

    def get_average_rating(self, obj):

        comments = obj.comments.all()

        if comments.exists():

            return round(

                sum(
                    comment.rating
                    for comment in comments
                ) / comments.count(),

                1

            )

        return 0


# =========================================
# BLOG DETAIL SERIALIZER
# =========================================

class BlogDetailSerializer(
    serializers.ModelSerializer
):

    author = AuthorSerializer(
        read_only=True
    )

    category = CategorySerializer(
        read_only=True
    )

    tags = TagSerializer(

        many=True,
        read_only=True

    )

    comments = CommentSerializer(

        many=True,
        read_only=True

    )

    likes_count = serializers.SerializerMethodField()

    bookmarks_count = serializers.SerializerMethodField()

    comments_count = serializers.SerializerMethodField()

    average_rating = serializers.SerializerMethodField()

    is_liked = serializers.SerializerMethodField()

    is_bookmarked = serializers.SerializerMethodField()

    class Meta:

        model = BlogPost

        fields = [

            'id',
            'title',
            'slug',
            'featured_image',
            'short_description',
            'content',
            'author',
            'category',
            'tags',
            'status',
            'views',
            'publish_at',
            'likes_count',
            'bookmarks_count',
            'comments_count',
            'average_rating',
            'is_liked',
            'is_bookmarked',
            'comments',
            'created_at',
            'updated_at',

        ]

    def get_likes_count(self, obj):

        return obj.likes.count()

    def get_bookmarks_count(self, obj):

        return obj.bookmarks.count()

    def get_comments_count(self, obj):

        return obj.comments.count()

    def get_average_rating(self, obj):

        comments = obj.comments.all()

        if comments.exists():

            return round(

                sum(
                    comment.rating
                    for comment in comments
                ) / comments.count(),

                1

            )

        return 0

    def get_is_liked(self, obj):

        request = self.context.get(
            'request'
        )

        if request and request.user.is_authenticated:

            return obj.likes.filter(
                id=request.user.id
            ).exists()

        return False

    def get_is_bookmarked(self, obj):

        request = self.context.get(
            'request'
        )

        if request and request.user.is_authenticated:

            return obj.bookmarks.filter(
                id=request.user.id
            ).exists()

        return False


# =========================================
# BLOG CREATE UPDATE SERIALIZER
# =========================================

class BlogCreateUpdateSerializer(
    serializers.ModelSerializer
):

    class Meta:

        model = BlogPost

        fields = [

            'title',
            'featured_image',
            'short_description',
            'content',
            'category',
            'tags',
            'status',
            'publish_at',

        ]

    def create(self, validated_data):

        validated_data['author'] = (
            self.context['request'].user
        )

        return super().create(
            validated_data
        )


# =========================================
# NOTIFICATION SERIALIZER
# =========================================

class NotificationSerializer(
    serializers.ModelSerializer
):

    sender = AuthorSerializer(
        read_only=True
    )

    post_title = serializers.CharField(
        source='post.title',
        read_only=True
    )

    class Meta:

        model = Notification

        fields = [

            'id',
            'sender',
            'post_title',
            'notification_type',
            'is_read',
            'created_at',

        ]