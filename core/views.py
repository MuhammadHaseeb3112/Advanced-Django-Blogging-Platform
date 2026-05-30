from django.shortcuts import render


# =========================================
# HOME PAGE
# =========================================

from django.core.cache import cache

from blog.models import BlogPost


def home(request):

    # =====================================
    # FEATURED POSTS
    # =====================================

    featured_posts = BlogPost.objects.published(
    ).optimized(
    ).with_likes_count(
    ).with_comments_count(
    )[:6]

    # =====================================
    # TRENDING POSTS FROM REDIS
    # =====================================

    trending_posts = cache.get(
        'trending_posts'
    )

    # =====================================
    # FALLBACK IF CACHE EMPTY
    # =====================================

    if not trending_posts:

        print(
            'TRENDING POSTS DB HIT 🔥'
        )

        trending_posts = BlogPost.objects.published(
        ).optimized(
        ).trending()[:5]

        cache.set(

            'trending_posts',

            trending_posts,

            timeout=60 * 60

        )

    else:

        print(
            'TRENDING POSTS CACHE HIT 🚀'
        )

    context = {

        'featured_posts': featured_posts,

        'trending_posts': trending_posts,

    }

    return render(

        request,

        'home.html',

        context

    )