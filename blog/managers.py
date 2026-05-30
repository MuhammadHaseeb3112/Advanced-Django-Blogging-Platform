from django.db import models
from django.utils import timezone

from django.db.models import (

    Count,
    Avg,
    Q,
    F,
    FloatField

)

from django.db.models.functions import (
    Coalesce
)


# =========================================
# BLOG POST QUERYSET
# =========================================

class BlogPostQuerySet(models.QuerySet):

    # =====================================
    # PUBLISHED POSTS
    # =====================================

    def published(self):

        return self.filter(

            status='published'

            ).filter(

                Q(publish_at__lte=timezone.now()) |

                Q(publish_at__isnull=True)

        )

    # =====================================
    # DRAFT POSTS
    # =====================================

    def drafts(self):

        return self.filter(
            status='draft'
        )

    # =====================================
    # POSTS BY AUTHOR
    # =====================================

    def by_author(self, user):

        return self.filter(
            author=user
        )

    # =====================================
    # TRENDING POSTS
    # =====================================

    def trending(self):

        return self.annotate(

            likes_count=Count(

                'likes',

                distinct=True

            ),

            comments_count=Count(

                'comments',

                distinct=True

            ),

            bookmarks_count=Count(

                'bookmarks',

                distinct=True

            ),

            avg_rating=Coalesce(

                Avg(
                    'comments__rating'
                ),

                0.0,

                output_field=FloatField()

            )

        ).annotate(

            trending_score=(

                F('likes_count') * 3

                +

                F('comments_count') * 5

                +

                F('bookmarks_count') * 4

                +

                F('avg_rating') * 2

                +

                F('views') * 2

            )

        ).order_by(

            '-trending_score',

            '-created_at'

        )

    # =====================================
    # POSTS WITH COMMENTS
    # =====================================

    def with_comments(self):

        return self.annotate(

            total_comments=Count(

                'comments',

                distinct=True

            )

        ).filter(

            total_comments__gt=0

        )

    # =====================================
    # POSTS WITH TOTAL LIKES
    # =====================================

    def with_likes_count(self):

        return self.annotate(

            likes_count=Count(

                'likes',

                distinct=True

            )

        )

    # =====================================
    # POSTS WITH TOTAL COMMENTS
    # =====================================

    def with_comments_count(self):

        return self.annotate(

            comments_count=Count(

                'comments',

                distinct=True

            )

        )

    # =====================================
    # POSTS WITH AVERAGE RATING
    # =====================================

    def with_average_rating(self):

        return self.annotate(

            average_rating=Coalesce(

                Avg(
                    'comments__rating'
                ),

                0.0,

                output_field=FloatField()

            )

        )

    # =====================================
    # GLOBAL SEARCH
    # =====================================

    def search(self, query):

        if not query:

            return self

        return self.filter(

            Q(title__icontains=query) |

            Q(short_description__icontains=query) |

            Q(content__icontains=query) |

            Q(category__name__icontains=query) |

            Q(tags__name__icontains=query)

        ).distinct()

    # =====================================
    # FILTER BY CATEGORY
    # =====================================

    def by_category(self, slug):

        if not slug:

            return self

        return self.filter(
            category__slug=slug
        )

    # =====================================
    # FILTER BY TAG
    # =====================================

    def by_tag(self, slug):

        if not slug:

            return self

        return self.filter(
            tags__slug=slug
        ).distinct()

    # =====================================
    # OPTIMIZED QUERYSET
    # =====================================

    def optimized(self):

        return self.select_related(

            'author',
            'category'

        ).prefetch_related(

            'tags',
            'likes',
            'bookmarks',
            'comments'

        )

    # =====================================
    # LATEST POSTS
    # =====================================

    def latest_posts(self):

        return self.order_by(
            '-created_at'
        )

    # =====================================
    # MOST COMMENTED POSTS
    # =====================================

    def most_commented(self):

        return self.with_comments_count(

        ).order_by(

            '-comments_count',
            '-created_at'

        )

    # =====================================
    # MOST LIKED POSTS
    # =====================================

    def most_liked(self):

        return self.with_likes_count(

        ).order_by(

            '-likes_count',
            '-created_at'

        )

    # =====================================
    # FEATURED POSTS
    # =====================================

    def featured(self):

        return self.published(

        ).with_likes_count(

        ).with_comments_count(

        ).order_by(

            '-likes_count',
            '-comments_count',
            '-created_at'

        )

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

            # =============================
            # SHARED TAGS
            # =============================

            shared_tags=Count(

                'tags',

                filter=Q(
                    tags__in=post.tags.all()
                ),

                distinct=True

            ),

            # =============================
            # ENGAGEMENT
            # =============================

            likes_count=Count(

                'likes',

                distinct=True

            ),

            comments_count=Count(

                'comments',

                distinct=True

            ),

            bookmarks_count=Count(

                'bookmarks',

                distinct=True

            ),

            # =============================
            # AVERAGE RATING
            # =============================

            avg_rating=Coalesce(

                Avg(
                    'comments__rating'
                ),

                0.0,

                output_field=FloatField()

            )

        ).annotate(

            # =============================
            # RECOMMENDATION SCORE
            # =============================

            recommendation_score=(

                F('shared_tags') * 5

                +

                F('likes_count') * 3

                +

                F('comments_count') * 4

                +

                F('bookmarks_count') * 4

                +

                F('avg_rating') * 2

                +

                F('views') * 2

            )

        ).order_by(

            '-recommendation_score',

            '-created_at'

        )


# =========================================
# BLOG POST MANAGER
# =========================================

class BlogPostManager(models.Manager):

    # =====================================
    # DEFAULT QUERYSET
    # =====================================

    def get_queryset(self):

        return BlogPostQuerySet(

            self.model,

            using=self._db

        )

    # =====================================
    # MANAGER METHODS
    # =====================================

    def published(self):

        return self.get_queryset().published()

    def drafts(self):

        return self.get_queryset().drafts()

    def by_author(self, user):

        return self.get_queryset().by_author(user)

    def trending(self):

        return self.get_queryset().trending()

    def with_comments(self):

        return self.get_queryset().with_comments()

    def with_likes_count(self):

        return self.get_queryset().with_likes_count()

    def with_comments_count(self):

        return self.get_queryset().with_comments_count()

    def with_average_rating(self):

        return self.get_queryset().with_average_rating()

    def search(self, query):

        return self.get_queryset().search(query)

    def by_category(self, slug):

        return self.get_queryset().by_category(slug)

    def by_tag(self, slug):

        return self.get_queryset().by_tag(slug)

    def optimized(self):

        return self.get_queryset().optimized()

    def latest_posts(self):

        return self.get_queryset().latest_posts()

    def most_commented(self):

        return self.get_queryset().most_commented()

    def most_liked(self):

        return self.get_queryset().most_liked()

    def featured(self):

        return self.get_queryset().featured()

    def recommended(self, post):

        return self.get_queryset().recommended(
            post
        )