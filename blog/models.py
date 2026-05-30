from django.db import models

from django.utils.text import slugify

from django.db.models import (
    Count,
    Avg,
    F,
    FloatField,
    Q
)

from django.db.models.functions import Coalesce

from django.core.validators import (

    MinValueValidator,
    MaxValueValidator

)

from accounts.models import CustomUser

from .managers import BlogPostManager


# =========================================
# CATEGORY MODEL
# =========================================

class Category(models.Model):

    name = models.CharField(

        max_length=100,

        unique=True

    )

    slug = models.SlugField(

        unique=True,

        blank=True

    )

    def save(self, *args, **kwargs):

        if not self.slug:

            self.slug = slugify(
                self.name
            )

        super().save(*args, **kwargs)

    def __str__(self):

        return self.name


# =========================================
# TAG MODEL
# =========================================

class Tag(models.Model):

    name = models.CharField(

        max_length=100,

        unique=True

    )

    slug = models.SlugField(

        unique=True,

        blank=True

    )

    def save(self, *args, **kwargs):

        if not self.slug:

            self.slug = slugify(
                self.name
            )

        super().save(*args, **kwargs)

    def __str__(self):

        return self.name


# =========================================
# BLOG POST MODEL
# =========================================

class BlogPost(models.Model):

    objects = BlogPostManager()

    STATUS_CHOICES = (

        ('draft', 'Draft'),

        ('published', 'Published'),

    )

    title = models.CharField(
        max_length=255
    )

    slug = models.SlugField(

        unique=True,

        blank=True

    )

    featured_image = models.ImageField(

        upload_to='blog_images/',

        blank=True,

        null=True

    )

    short_description = models.TextField(

        blank=True,

        null=True

    )

    content = models.TextField()

    author = models.ForeignKey(

        CustomUser,

        on_delete=models.CASCADE,

        related_name='posts'

    )

    likes = models.ManyToManyField(

        CustomUser,

        blank=True,

        related_name='liked_posts'

    )

    bookmarks = models.ManyToManyField(

        CustomUser,

        blank=True,

        related_name='bookmarked_posts'

    )

    category = models.ForeignKey(

        Category,

        on_delete=models.SET_NULL,

        null=True,

        blank=True,

        related_name='posts'

    )

    tags = models.ManyToManyField(

        Tag,

        blank=True,

        related_name='posts'

    )

    status = models.CharField(

        max_length=20,

        choices=STATUS_CHOICES,

        default='draft'

    )

    publish_at = models.DateTimeField(

    null=True,

    blank=True

)

    views = models.PositiveIntegerField(
    default=0
)

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:

        ordering = ['-created_at']

    def __str__(self):

        return self.title


    # =====================================
    # RECOMMENDED POSTS
    # =====================================



    def recommended(self, post):

        return self.published(

    ).optimized(

    ).exclude(

        id=post.id

    ).filter(

        category=post.category

    ).annotate(

        shared_tags=Count(

            'tags',

            filter=Q(
                tags__in=post.tags.all()
            )

        ),

        likes_count=Count(
            'likes'
        ),

        comments_count=Count(
            'comments'
        ),

        avg_rating=Coalesce(

            Avg(
                'comments__rating'
            ),

            0.0,

            output_field=FloatField()

        )

    ).annotate(

        recommendation_score=(

            F('shared_tags') * 5

            +

            F('likes_count') * 3

            +

            F('comments_count') * 2

            +

            F('avg_rating') * 2

        )

    ).order_by(

        '-recommendation_score',

        '-created_at'

    )



# =========================================
# COMMENT MODEL
# =========================================

class Comment(models.Model):

    post = models.ForeignKey(

        BlogPost,

        on_delete=models.CASCADE,

        related_name='comments'

    )

    author = models.ForeignKey(

        CustomUser,

        on_delete=models.CASCADE,

        related_name='comments'

    )

    rating = models.PositiveIntegerField(

        validators=[

            MinValueValidator(1),

            MaxValueValidator(5),

        ],

        default=5

    )

    content = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:

        ordering = ['-created_at']

    def __str__(self):

        return f"{self.author} - {self.post}"


# =========================================
# NOTIFICATION MODEL
# =========================================

class Notification(models.Model):

    NOTIFICATION_TYPES = (

        ('like', 'Like'),

        ('comment', 'Comment'),

    )

    sender = models.ForeignKey(

        CustomUser,

        on_delete=models.CASCADE,

        related_name='sent_notifications'

    )

    receiver = models.ForeignKey(

        CustomUser,

        on_delete=models.CASCADE,

        related_name='notifications'

    )

    post = models.ForeignKey(

        BlogPost,

        on_delete=models.CASCADE,

        related_name='notifications'

    )

    notification_type = models.CharField(

        max_length=20,

        choices=NOTIFICATION_TYPES

    )

    is_read = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:

        ordering = ['-created_at']

    def __str__(self):

        return f'{self.sender} -> {self.receiver}'