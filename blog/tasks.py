from celery import shared_task

import logging

from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.core.cache import cache
from django.core.mail import EmailMultiAlternatives
from django.core.mail import send_mail
from django.db.models import (
    Avg,
    Count,
    F,
    FloatField,
    Sum,
)
from django.db.models.functions import Coalesce
from django.utils import timezone

from accounts.models import CustomUser

from .models import (
    BlogPost,
    Category,
    Comment,
    Notification,
    Tag,
)

# =========================================
# LOGGER CONFIGURATION
# =========================================

logger = logging.getLogger(__name__)

User = get_user_model()

# =========================================
# WELCOME EMAIL TASK
# =========================================


@shared_task(bind=True, max_retries=3)
def send_welcome_email(self, username, user_email):

    try:

        logger.info(
            f"Sending welcome email to {user_email}"
        )

        subject = "Welcome to DjangoBlog 🚀"

        message = f"""
Hi {username},

Welcome to DjangoBlog.

Your account was created successfully.

Start exploring blogs,
writing posts,
and engaging with the community.

🚀 DjangoBlog Team
"""

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user_email],
            fail_silently=False,
        )

        logger.info(
            f"Welcome email sent successfully to {user_email}"
        )

        return "Email sent successfully"

    except Exception as exc:

        logger.error(
            f"Welcome email failed: {str(exc)}"
        )

        raise self.retry(
            exc=exc,
            countdown=60
        )


# =========================================
# CALCULATE TRENDING POSTS
# =========================================


@shared_task
def calculate_trending_posts():

    logger.info(
        "Calculating trending posts..."
    )

    try:

        trending_posts = (

            BlogPost.objects.published()

            .annotate(

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
                    Avg('comments__rating'),
                    0.0,
                    output_field=FloatField()
                )

            )

            .annotate(

                trending_score=(

                    F('likes_count') * 3

                    +

                    F('comments_count') * 5

                    +

                    F('avg_rating') * 2

                    +

                    F('bookmarks_count') * 4

                    +

                    F('views') * 2

                )

            )

            .order_by(
                '-trending_score',
                '-created_at'
            )[:5]

        )

        cache.set(
            'trending_posts',
            trending_posts,
            timeout=60 * 60
        )

        logger.info(
            "Trending posts cached successfully"
        )

        return "Trending posts updated"

    except Exception as exc:

        logger.error(
            f"Trending posts task failed: {str(exc)}"
        )

        raise exc


# =========================================
# DELETE OLD NOTIFICATIONS
# =========================================


@shared_task
def delete_old_notifications():

    logger.info(
        "Deleting old notifications..."
    )

    try:

        old_notifications = Notification.objects.filter(
            created_at__lt=timezone.now() - timedelta(days=7)
        )

        deleted_count = old_notifications.count()

        old_notifications.delete()

        logger.info(
            f"{deleted_count} old notifications deleted"
        )

        return f"{deleted_count} old notifications deleted"

    except Exception as exc:

        logger.error(
            f"Delete notifications task failed: {str(exc)}"
        )

        raise exc


# =========================================
# WEEKLY BLOG RECOMMENDATIONS
# =========================================


@shared_task(bind=True, max_retries=3)
def send_weekly_blog_recommendations(self):

    logger.info(
        "Sending weekly blog recommendations..."
    )

    try:

        trending_posts = (
            BlogPost.objects.published().trending()[:5]
        )

        current_site = Site.objects.get_current()

        domain = f"http://{current_site.domain}"

        users = User.objects.filter(
            is_active=True
        ).exclude(email='')

        for user in users:

            subject = "🔥 Weekly Blog Recommendations"

            text_content = "Top blogs this week:\n\n"

            html_content = """
            <h2>🔥 Top Blogs This Week</h2>
            <ul>
            """

            for post in trending_posts:

                blog_url = (
                    f"{domain}/blogs/{post.slug}/"
                )

                text_content += (
                    f"- {post.title}\n"
                    f"{blog_url}\n\n"
                )

                html_content += f"""
                <li>
                    <a href="{blog_url}">
                        {post.title}
                    </a>
                </li>
                """

            html_content += """
            </ul>

            <br>

            <p>
                Read more on <b>DjangoBlog 🚀</b>
            </p>
            """

            email = EmailMultiAlternatives(

                subject=subject,

                body=text_content,

                from_email=settings.DEFAULT_FROM_EMAIL,

                to=[user.email],

            )

            email.attach_alternative(
                html_content,
                "text/html"
            )

            email.send()

            logger.info(
                f"Weekly recommendation sent to {user.email}"
            )

        return "Weekly recommendation emails sent"

    except Exception as exc:

        logger.error(
            f"Weekly recommendation task failed: {str(exc)}"
        )

        raise self.retry(
            exc=exc,
            countdown=120
        )


# =========================================
# PUBLISH SCHEDULED POSTS
# =========================================


@shared_task
def publish_scheduled_posts():

    logger.info(
        "Checking scheduled posts..."
    )

    try:

        posts = BlogPost.objects.optimized().filter(

            status='draft',

            publish_at__isnull=False,

            publish_at__lte=timezone.now()

        )

        count = posts.count()

        for post in posts:

            post.status = 'published'

            post.save(
                update_fields=[
                    'status',
                    'updated_at'
                ]
            )

            logger.info(
                f"Published post: {post.title}"
            )

        logger.info(
            f"{count} scheduled posts published"
        )

        return f"{count} posts published"

    except Exception as exc:

        logger.error(
            f"Scheduled publish task failed: {str(exc)}"
        )

        raise exc


# =========================================
# DASHBOARD ANALYTICS CACHE
# =========================================


@shared_task
def calculate_dashboard_analytics():

    logger.info(
        "Calculating dashboard analytics..."
    )

    try:

        total_users = CustomUser.objects.count()

        total_posts = BlogPost.objects.count()

        total_comments = Comment.objects.count()

        total_categories = Category.objects.count()

        total_tags = Tag.objects.count()

        total_views = BlogPost.objects.aggregate(
            total_views=Sum('views')
        )['total_views'] or 0

        total_likes = sum(
            post.likes.count()
            for post in BlogPost.objects.all()
        )

        total_bookmarks = sum(
            post.bookmarks.count()
            for post in BlogPost.objects.all()
        )

        trending_posts = list(

            BlogPost.objects.trending()

            .values(
                'title',
                'slug',
                'views'
            )[:5]

        )

        top_categories = list(

            Category.objects.annotate(

                total_posts=Count('posts')

            )

            .values(
                'name',
                'total_posts'
            )

            .order_by(
                '-total_posts'
            )[:5]

        )

        analytics_data = {

            'total_users': total_users,

            'total_posts': total_posts,

            'total_comments': total_comments,

            'total_categories': total_categories,

            'total_tags': total_tags,

            'total_views': total_views,

            'total_likes': total_likes,

            'total_bookmarks': total_bookmarks,

            'trending_posts': trending_posts,

            'top_categories': top_categories,

        }

        cache.set(
            'dashboard_analytics',
            analytics_data,
            timeout=None
        )

        logger.info(
            "Dashboard analytics cached successfully"
        )

        return "Dashboard analytics updated"

    except Exception as exc:

        logger.error(
            f"Dashboard analytics task failed: {str(exc)}"
        )

        raise exc