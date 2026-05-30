from django.shortcuts import (

    render,
    redirect,
    get_object_or_404

)


from django.views.generic import (

    ListView,
    DetailView

)

from django.contrib.auth.decorators import (
    login_required
)


from django.core.paginator import (
    Paginator
)

from .models import (

    BlogPost,
    Comment,
    Category,
    Tag,
    Notification,


)

from accounts.models import CustomUser
from django.http import JsonResponse

from django.template.loader import render_to_string
from django.contrib.admin.views.decorators import staff_member_required

from django.contrib import messages
from django.core.cache import cache

from django.db.models import Q, F,Sum

from django.db.models import Count

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.utils import timezone
import json





# =========================================
# CLEAR BLOG CACHE
# =========================================

def clear_blog_cache():

    cache.clear()

    print(
        'BLOG CACHE CLEARED 🚀'
    )



# =========================================
# AUTHOR OR ADMIN CHECK
# =========================================

def author_required(view_func):

    def wrapper(request, *args, **kwargs):

        if not request.user.is_authenticated:

            return redirect(
                'login'
        )

        if request.user.role not in [

            'admin',
            'author'

        ]:

            messages.error(

                request,

                'Only authors can access this page.'

            )

            return redirect(

                'blog_list'

            )

        return view_func(

            request,
            *args,
            **kwargs

        )

    return wrapper

# =========================================
# BLOG LIST VIEW
# GLOBAL SEARCH SYSTEM
# =========================================


class BlogListView(
    ListView
):

    model = BlogPost

    template_name = 'blog/blog_list.html'

    context_object_name = 'posts'

    paginate_by = 9

    def get_queryset(self):

        # =====================================
        # REQUEST PARAMETERS
        # =====================================

        search = self.request.GET.get(
            'search',
            ''
        ).strip()

        category = self.request.GET.get(
            'category',
            ''
        ).strip()

        tag = self.request.GET.get(
            'tag',
            ''
        ).strip()

        page = self.request.GET.get(
            'page',
            1
        )

        # =====================================
        # UNIQUE CACHE KEY
        # =====================================

        cache_key = (

            f'blog_list_'

            f'{search}_'

            f'{category}_'

            f'{tag}_'

            f'page_{page}'

        )

        # =====================================
        # CHECK REDIS CACHE
        # =====================================

        cached_queryset = cache.get(
            cache_key
        )

        if cached_queryset:

            print(
                'CACHE HIT 🚀'
            )

            return cached_queryset

        print(
            'DATABASE HIT 🔥'
        )

        # =====================================
        # BASE QUERYSET
        # =====================================

        queryset = BlogPost.objects.published(
        ).optimized(
        ).with_likes_count(
        ).with_comments_count(
        ).with_average_rating()

        # =====================================
        # GLOBAL SEARCH
        # =====================================

        if search:

            queryset = queryset.search(
                search
            )

        # =====================================
        # CATEGORY FILTER
        # =====================================

        if category:

            queryset = queryset.by_category(
                category
            )

        # =====================================
        # TAG FILTER
        # =====================================

        if tag:

            queryset = queryset.by_tag(
                tag
            )

        queryset = queryset.distinct().order_by(
    '-created_at'
)

        # =====================================
        # SAVE QUERYSET TO REDIS
        # =====================================

        cache.set(

            cache_key,

            queryset,

            timeout=60 * 5

        )

        return queryset

    # =========================================
    # CONTEXT
    # =========================================

    def get_context_data(self, **kwargs):

        context = super().get_context_data(
            **kwargs
        )

        # =====================================
        # CACHED CATEGORIES
        # =====================================

        categories = cache.get(
            'all_categories'
        )

        if not categories:

            print(
                'CATEGORIES DB HIT 🔥'
            )

            categories = Category.objects.all()

            cache.set(

                'all_categories',

                categories,

                timeout=60 * 30

            )

        else:

            print(
                'CATEGORIES CACHE HIT 🚀'
            )

        # =====================================
        # CACHED TAGS
        # =====================================

        tags = cache.get(
            'all_tags'
        )

        if not tags:

            print(
                'TAGS DB HIT 🔥'
            )

            tags = Tag.objects.all()

            cache.set(

                'all_tags',

                tags,

                timeout=60 * 30

            )

        else:

            print(
                'TAGS CACHE HIT 🚀'
            )

        # =====================================
        # CONTEXT DATA
        # =====================================

        context['categories'] = categories

        context['tags'] = tags

        context['search_query'] = self.request.GET.get(
            'search',
            ''
        )

        context['selected_category'] = self.request.GET.get(
            'category',
            ''
        )

        context['selected_tag'] = self.request.GET.get(
            'tag',
            ''
        )

        context['results_count'] = self.get_queryset().count()

        return context


# =========================================
# BLOG DETAIL VIEW
# =========================================

class BlogDetailView(

    DetailView

):

    model = BlogPost

    template_name = 'blog/blog_detail.html'

    context_object_name = 'post'

    slug_field = 'slug'

    slug_url_kwarg = 'slug'

    # =====================================
    # QUERYSET
    # =====================================

    def get_queryset(self):

        return BlogPost.objects.published(

        ).optimized(

        ).with_average_rating()

    # =====================================
    # UNIQUE VIEW COUNTER
    # =====================================

    def get_object(self, queryset=None):

        obj = super().get_object(
            queryset
        )

        viewed_posts = self.request.session.get(

            'viewed_posts',

            []

        )

        if obj.id not in viewed_posts:

            BlogPost.objects.filter(

                id=obj.id

            ).update(

                views=F('views') + 1

            )

            viewed_posts.append(
                obj.id
            )

            self.request.session[
                'viewed_posts'
            ] = viewed_posts

            print(
                'UNIQUE VIEW COUNTED 🚀'
            )

        else:

            print(
                'DUPLICATE VIEW BLOCKED 🚫'
            )

        obj.refresh_from_db()

        return obj

    # =====================================
    # RECOMMENDED POSTS
    # =====================================

    def get_context_data(self, **kwargs):

        context = super().get_context_data(
            **kwargs
        )

        related_posts = BlogPost.objects.recommended(

            self.object

        )[:4]

        # =================================
        # FALLBACK TO TRENDING
        # =================================

        if not related_posts.exists():

            related_posts = BlogPost.objects.trending(

            ).exclude(

                id=self.object.id

            )[:4]

        context['related_posts'] = related_posts

        return context

# =========================================
# CATEGORY POSTS
# =========================================

def category_posts(request, slug):

    category = get_object_or_404(

        Category,

        slug=slug

    )

    posts = BlogPost.objects.published(
    ).optimized(
    ).with_likes_count(
    ).with_comments_count(
    ).filter(

        category=category

    )

    # =====================================
    # SEARCH INSIDE CATEGORY
    # =====================================

    search = request.GET.get(
        'search'
    )

    if search:

        search = search.strip()

        posts = posts.filter(

            title__icontains=search

        )

    # =====================================
    # TAG FILTER
    # =====================================

    tag = request.GET.get(
        'tag'
    )

    if tag:

        posts = posts.by_tag(
            tag
        )

    posts = posts.distinct()

    paginator = Paginator(

        posts,
        9

    )

    page_number = request.GET.get(
        'page'
    )

    page_obj = paginator.get_page(
        page_number
    )

    context = {

        'category': category,

        'posts': page_obj,

        'page_obj': page_obj,

        'tags': Tag.objects.all(),

        'search_query': search,

        'selected_tag': tag,

        'results_count': paginator.count,

    }

    return render(

        request,

        'blog/category_posts.html',

        context

    )


# =========================================
# TAG POSTS
# =========================================

def tag_posts(request, slug):

    tag = get_object_or_404(

        Tag,

        slug=slug

    )

    posts = BlogPost.objects.published(
    ).optimized(
    ).with_likes_count(
    ).with_comments_count(
    ).filter(

        tags=tag

    ).distinct()

    # =====================================
    # SEARCH INSIDE TAG
    # =====================================

    search = request.GET.get(
        'search'
    )

    if search:

        search = search.strip()

        posts = posts.filter(

            title__icontains=search

        )

    paginator = Paginator(

        posts,
        9

    )

    page_number = request.GET.get(
        'page'
    )

    page_obj = paginator.get_page(
        page_number
    )

    context = {

        'tag': tag,

        'posts': page_obj,

        'page_obj': page_obj,

        'search_query': search,

        'results_count': paginator.count,

    }

    return render(

        request,

        'blog/tag_posts.html',

        context

    )


# =========================================
# AJAX BOOKMARK SYSTEM
# =========================================

@login_required
def bookmark_post(request, slug):

    if request.method != 'POST':

        return JsonResponse({

            'success': False,
            'message': 'Invalid request'

        }, status=400)

    post = get_object_or_404(

        BlogPost.objects.published(),
        slug=slug

    )

    bookmarked = False

    # =====================================
    # REMOVE BOOKMARK
    # =====================================

    if request.user in post.bookmarks.all():

        post.bookmarks.remove(request.user)

    # =====================================
    # ADD BOOKMARK
    # =====================================

    else:

        post.bookmarks.add(request.user)

        bookmarked = True


    clear_blog_cache()

    # =====================================
    # REALTIME BOOKMARK UPDATE
    # =====================================

    channel_layer = get_channel_layer()

    async_to_sync(
        channel_layer.group_send
    )(
        f'blog_{post.id}',

        {

            'type': 'bookmark_update',

            'bookmarks_count': (

                post.bookmarks.count()

            ),

        }

    )

    return JsonResponse({

        'success': True,

        'bookmarked': bookmarked,

        'total_bookmarks': (

            post.bookmarks.count()

        ),

    })

# =========================================
# AJAX LIKE POST
# =========================================

@login_required
def like_post(request, slug):

    if request.method != 'POST':

        return JsonResponse({

            'success': False,
            'message': 'Invalid request method'

        }, status=400)

    post = get_object_or_404(

        BlogPost.objects.published(),
        slug=slug

    )

    liked = False

    # =====================================
    # REMOVE LIKE
    # =====================================

    if post.likes.filter(id=request.user.id).exists():

        post.likes.remove(request.user)

        # DELETE OLD LIKE NOTIFICATION

        Notification.objects.filter(

            sender=request.user,
            receiver=post.author,
            post=post,
            notification_type='like'

        ).delete()

    # =====================================
    # ADD LIKE
    # =====================================

    else:

        post.likes.add(request.user)

        liked = True

        # CREATE NOTIFICATION ONLY ONCE

        if request.user != post.author:

            notification_exists = Notification.objects.filter(

                sender=request.user,
                receiver=post.author,
                post=post,
                notification_type='like'

            ).exists()

            if not notification_exists:

                Notification.objects.create(

                    receiver=post.author,
                    sender=request.user,
                    notification_type='like',
                    post=post

                )

            # =====================================
            # REALTIME NOTIFICATION
            # =====================================

            unread_count = Notification.objects.filter(

                receiver=post.author,
                is_read=False

            ).count()

            channel_layer = get_channel_layer()

            async_to_sync(
                channel_layer.group_send
            )(

                f'user_{post.author.id}',

                {

                    'type': 'send_notification',

                    'message': f'{request.user.username} liked your post ❤️',

                    'unread_count': unread_count,

                }

            )

    clear_blog_cache()

    # =====================================
    # REALTIME LIKE UPDATE
    # =====================================

    channel_layer = get_channel_layer()

    async_to_sync(
        channel_layer.group_send
    )(
        f'blog_{post.id}',

        {

            'type': 'like_update',

            'likes_count': (

                post.likes.count()

            ),

        }

    )

    return JsonResponse({

        'success': True,

        'liked': liked,

        'total_likes': (

            post.likes.count()

        ),

    })

# =========================================
# AJAX COMMENT SYSTEM
# =========================================

@login_required
def add_comment(request, slug):

    if request.method != 'POST':

        return JsonResponse({

            'success': False,
            'message': 'Invalid request'

        }, status=400)

    post = get_object_or_404(

        BlogPost.objects.published(),
        slug=slug

    )

    content = request.POST.get(

        'content'

    )

    rating = request.POST.get(

        'rating'

    )

    # =====================================
    # VALIDATION
    # =====================================

    if not content:

        return JsonResponse({

            'success': False,
            'message': 'Comment cannot be empty'

        }, status=400)

    # =====================================
    # CREATE COMMENT
    # =====================================

    comment = Comment.objects.create(

        post=post,
        author=request.user,
        content=content,
        rating=rating

    )

    clear_blog_cache()

    # =====================================
    # CHANNEL LAYER
    # =====================================

    channel_layer = get_channel_layer()

    # =====================================
    # CREATE NOTIFICATION
    # =====================================

    if request.user != post.author:

        Notification.objects.create(

            receiver=post.author,
            sender=request.user,
            notification_type='comment',
            post=post

        )

        unread_count = Notification.objects.filter(

            receiver=post.author,
            is_read=False

        ).count()

        # =====================================
        # REALTIME NOTIFICATION
        # =====================================

        async_to_sync(
            channel_layer.group_send
        )(

            f'user_{post.author.id}',

            {

                'type': 'send_notification',

                'message': f'{request.user.username} commented on your post 💬',

                'unread_count': unread_count,

            }

        )

    # =====================================
    # RENDER COMMENT HTML
    # =====================================

    html = render_to_string(

        'includes/comment_card.html',

        {

            'comment': comment

        },

        request=request

    )

    # =====================================
    # REALTIME COMMENT UPDATE
    # =====================================

    async_to_sync(
        channel_layer.group_send
    )(
        f'blog_{post.id}',

        {

            'type': 'comment_update',

            'comments_count': (

                post.comments.count()

            ),

            'comment_html': html,

        }

    )

    return JsonResponse({

        'success': True,

        'comment_html': html,

        'total_comments': (

            post.comments.count()

        ),

    })

    
# =========================================
# DASHBOARD
# =========================================

@login_required
def dashboard(request):

    user = request.user

    # =====================================
    # REDIS ANALYTICS CACHE
    # =====================================

    analytics = cache.get(

        'dashboard_analytics',

        {}

    )

    # =====================================
    # USER POSTS    
    # =====================================

    user_posts = BlogPost.objects.by_author(
        user
    ).optimized()

    # =====================================
    # OPTIMIZED ENGAGEMENT
    # =====================================

    annotated_posts = user_posts.annotate(

        likes_total=Count(
            'likes',
            distinct=True
        ),

        comments_total=Count(
            'comments',
            distinct=True
        )
    )

    # =====================================
    # PLATFORM TOTALS
    # =====================================

    total_platform_likes = sum(

        BlogPost.objects.annotate(
            likes_count=Count('likes')
        ).values_list(
            'likes_count',
            flat=True
        )

    )

    total_platform_bookmarks = sum(

        BlogPost.objects.annotate(
            bookmarks_count=Count('bookmarks')
        ).values_list(
            'bookmarks_count',
            flat=True
        )

    )


    # =====================================
    # AUTHOR ENGAGEMENT
    # =====================================

    total_post_likes = sum(
        post.likes.count()
        for post in user_posts
    )

    total_post_comments = Comment.objects.filter(
        post__author=user
    ).count()

    # =====================================
    # USER ACTIVITY
    # =====================================

    liked_posts = BlogPost.objects.filter(

        likes=user

    )

    commented_posts = BlogPost.objects.filter(

        comments__author=user

    ).distinct()

    saved_posts = user.bookmarked_posts.all()



    # =====================================
    # TOP CATEGORIES JSON
    # =====================================

    top_categories = analytics.get(

        'top_categories',

        []

    )

    top_categories_labels = json.dumps([

        category['name']

        for category in top_categories

    ])

    top_categories_counts = json.dumps([

        category['total_posts']

        for category in top_categories

    ])




    # =====================================
    # TRENDING POSTS
    # =====================================

    trending_posts = BlogPost.objects.filter(
        status='published'
    ).order_by(
        '-views'
    )[:5]

    

    # =====================================
    # BASE CONTEXT
    # =====================================

    context = {
            # User Activity
        'total_liked': liked_posts.count(),
        'total_saved': saved_posts.count(),
        'total_commented': commented_posts.count(),

        'my_posts_likes': total_post_likes,
        'my_posts_comments': total_post_comments,

        

        # Real-time Platform Stats
        'total_users': CustomUser.objects.count(),
        'total_blog_posts': BlogPost.objects.count(),
        'total_platform_comments': Comment.objects.count(),
        'total_platform_likes': total_platform_likes,
        'total_platform_bookmarks': total_platform_bookmarks,
        'total_categories': Category.objects.count(),
        'total_tags': Tag.objects.count(),
        'total_views': BlogPost.objects.aggregate(
            total=Sum('views')
        )['total'] or 0,

        # Charts
        'top_categories': top_categories,
        'top_categories_labels': top_categories_labels,
        'top_categories_counts': top_categories_counts,
        'trending_posts': trending_posts,
    }

    # =====================================
    # AUTHOR + ADMIN
    # =====================================

    if user.role in ['author', 'admin']:

        context.update({

            # =================================
            # POSTS
            # =================================

            'total_posts': user_posts.count(),

            'published_posts_count': user_posts.filter(

                status='published'

            ).count(),

            'draft_posts_count': user_posts.filter(

                status='draft'

            ).count(),

            'scheduled_posts_count': user_posts.filter(

                status='draft',

                publish_at__gt=timezone.now()

            ).count(),


        })

    # =====================================
    # AUTHOR
    # =====================================

    if user.role == 'author':

        context.update({

            'is_author': True,

        })

    # =====================================
    # ADMIN
    # =====================================

    elif user.role == 'admin':

        context.update({

            'is_admin': True,

            # =================================
            # PLATFORM STATS
            # =================================

            'total_users': analytics.get(

                'total_users',

                0

            ),

            'total_blog_posts': analytics.get(

                'total_posts',

                0

            ),

            'total_platform_comments': analytics.get(

                'total_comments',

                0

            ),

            'total_categories': analytics.get(

                'total_categories',

                0

            ),

            'total_tags': analytics.get(

                'total_tags',

                0

            ),

        })

    # =====================================
    # SIMPLE USER
    # =====================================

    else:

        context.update({

            'is_user': True,

        })

    return render(

        request,

        'blog/dashboard.html',

        context

    )

    
# =========================================
# SAVED POSTS
# =========================================

@login_required
def saved_posts(request):

    posts = request.user.bookmarked_posts.all(
    ).select_related(

        'author',
        'category'

    ).prefetch_related(

        'tags',
        'likes',
        'comments'

    )

    context = {

        'posts': posts

    }

    return render(

        request,

        'blog/saved_posts.html',

        context

    )


# =========================================
# PROFILE VIEW
# =========================================

@login_required
def profile_view(request):

    user = request.user

    user_posts = BlogPost.objects.by_author(
        user
    ).optimized()

    bookmarked_posts = user.bookmarked_posts.all()

    liked_posts = BlogPost.objects.filter(
        likes=user
    )

    commented_posts = BlogPost.objects.filter(
        comments__author=user
    ).distinct()

    if request.method == 'POST':

        username = request.POST.get(
        'username'
        ).strip()

        if not username:

            messages.error(

            request,

            'Username is required.'

            )

            return redirect(
                'profile'
            )

        user.username = username

        email = request.POST.get('email')

        if CustomUser.objects.exclude(

            id=user.id

        ).filter(

        email=email

        ).exists():

            messages.error(

            request,

            'Email already exists.'

        )

            return redirect('profile')

        user.email = email

        profile_image = request.FILES.get(
            'profile_image'
        )

        if profile_image:

            user.profile_image = profile_image

        user.save()

        messages.success(

            request,

            'Profile updated successfully.'

        )

        return redirect(
            'profile'
        )

    context = {

        'user_posts': user_posts,

        'bookmarked_posts': bookmarked_posts,

        'liked_posts': liked_posts,

        'commented_posts': commented_posts,

    }

    return render(

        request,

        'blog/profile.html',

        context

    )


# =========================================
# MY POSTS
# =========================================

@login_required
def my_posts(request):

    posts = BlogPost.objects.by_author(
        request.user
    ).optimized(
    ).with_likes_count(
    ).with_comments_count(
    ).with_average_rating()

    # =====================================
    # SEARCH
    # =====================================

    search = request.GET.get(
        'search'
    )

    if search:

        search = search.strip()

        posts = posts.filter(

            Q(title__icontains=search) |

            Q(short_description__icontains=search)

        )

    # =====================================
    # STATUS FILTER
    # =====================================

    status = request.GET.get(
        'status'
    )

    if status:

        posts = posts.filter(
            status=status
        )

    posts = posts.distinct()

    # =====================================
    # PAGINATION
    # =====================================

    paginator = Paginator(

        posts,
        9

    )

    page_number = request.GET.get(
        'page'
    )

    page_obj = paginator.get_page(
        page_number
    )

    context = {

        'posts': page_obj,

        'page_obj': page_obj,

        'search_query': search,

        'selected_status': status,

        'results_count': paginator.count,

    }

    return render(

        request,

        'blog/my_posts.html',

        context

    )

# =========================================
# CREATE POST
# =========================================

@login_required
@author_required
def create_post(request):

    categories = Category.objects.all()

    tags = Tag.objects.all()

    if request.method == 'POST':

        title = request.POST.get(
            'title'
        )

        short_description = request.POST.get(
            'short_description'
        )

        content = request.POST.get(
            'content'
        )

        featured_image = request.FILES.get(
            'featured_image'
        )

        category_id = request.POST.get(
            'category'
        )

        selected_tags = request.POST.getlist(
            'tags'
        )

        status = request.POST.get(
            'status'
        )

        publish_at = request.POST.get(
            'publish_at'
        )

        # =================================
        # VALIDATION
        # =================================

        if not title or not content:

            messages.error(

                request,

                'Title and content are required.'

            )

            return redirect(
                'create_post'
            )

        # =================================
        # AUTO PUBLISH TIME
        # =================================

        if status == 'published' and not publish_at:

            publish_at = timezone.now()

        # =================================
        # CATEGORY
        # =================================

        category = None

        if category_id:

            category = get_object_or_404(

                Category,

                id=category_id

            )

        # =================================
        # CREATE POST
        # =================================

        post = BlogPost.objects.create(

            title=title,

            short_description=short_description,

            content=content,

            featured_image=featured_image,

            category=category,

            author=request.user,

            status=status,

            publish_at=publish_at

        )

        # =================================
        # TAGS
        # =================================

        if selected_tags:

            post.tags.set(
                selected_tags
            )

        
        clear_blog_cache()


        # =================================
        # SUCCESS MESSAGE
        # =================================

        messages.success(

            request,

            'Post created successfully.'

        )

        return redirect(
            'my_posts'
        )

    context = {

        'categories': categories,

        'tags': tags,

    }

    return render(

        request,

        'blog/create_post.html',

        context

    )


# =========================================
# UPDATE POST
# =========================================

@login_required
@author_required
def update_post(request, slug):

    post = get_object_or_404(

        BlogPost.objects.optimized(),

        slug=slug

    )

    # =====================================
    # PERMISSION
    # =====================================

    if request.user != post.author and not request.user.is_superuser:

        messages.error(

            request,

            'You do not have permission.'

        )

        return redirect(
            'dashboard'
        )

    categories = Category.objects.all()

    tags = Tag.objects.all()

    if request.method == 'POST':

        title = request.POST.get(
            'title'
        )

        short_description = request.POST.get(
            'short_description'
        )

        content = request.POST.get(
            'content'
        )

        status = request.POST.get(
            'status'
        )

        publish_at = request.POST.get(
            'publish_at'
        )

        # =================================
        # VALIDATION
        # =================================

        if not title or not content:

            messages.error(

                request,

                'Title and content are required.'

            )

            return redirect(
                'update_post',
                slug=post.slug
            )

        # =================================
        # AUTO PUBLISH TIME
        # =================================

        if status == 'published' and not publish_at:

            publish_at = timezone.now()

        # =================================
        # UPDATE FIELDS
        # =================================

        post.title = title

        post.short_description = short_description

        post.content = content

        post.status = status

        post.publish_at = publish_at

        # =================================
        # CATEGORY
        # =================================

        category_id = request.POST.get(
            'category'
        )

        if category_id:

            post.category = get_object_or_404(

                Category,

                id=category_id

            )

        else:

            post.category = None

        # =================================
        # FEATURED IMAGE
        # =================================

        featured_image = request.FILES.get(
            'featured_image'
        )

        if featured_image:

            post.featured_image = featured_image

        # =================================
        # SAVE POST
        # =================================

        post.save()

        # =================================
        # TAGS
        # =================================

        selected_tags = request.POST.getlist(
            'tags'
        )

        post.tags.set(
            selected_tags
        )

        clear_blog_cache()


        # =================================
        # SUCCESS MESSAGE
        # =================================

        messages.success(

            request,

            'Post updated successfully.'

        )

        return redirect(
            'my_posts'
        )

    context = {

        'post': post,

        'categories': categories,

        'tags': tags,

    }

    return render(

        request,

        'blog/update_post.html',

        context

    )


# =========================================
# DELETE POST
# =========================================

@login_required
@author_required
def delete_post(request, slug):

    post = get_object_or_404(

        BlogPost.objects.optimized(),

        slug=slug

    )

    # =====================================
    # PERMISSION
    # =====================================

    if request.user != post.author and not request.user.is_superuser:

        return redirect(
            'dashboard'
        )

    if request.method == 'POST':

        post.delete()


        clear_blog_cache()


        messages.success(

            request,

            'Post deleted successfully.'

        )

        return redirect(
            'my_posts'
        )

    context = {

        'post': post

    }

    return render(

        request,

        'blog/delete_post.html',

        context

    )


# =========================================
# MANAGE CATEGORIES
# =========================================

@staff_member_required
@login_required
def manage_categories(request):

    if not request.user.is_superuser:

        return redirect(
            'dashboard'
        )

    # =====================================
    # EDIT CATEGORY
    # =====================================

    edit_id = request.GET.get(
        'edit'
    )

    edit_category = None

    if edit_id:

        edit_category = get_object_or_404(

            Category,

            id=edit_id

        )

    # =====================================
    # POST ACTIONS
    # =====================================

    if request.method == 'POST':

        # DELETE CATEGORY

        delete_id = request.POST.get(
            'delete_category_id'
        )

        if delete_id:

            category = get_object_or_404(

                Category,

                id=delete_id

            )

            category.delete()

            clear_blog_cache()



            messages.success(

                request,

                'Category deleted successfully.'

            )

            return redirect(
                'manage_categories'
            )

        # CREATE / UPDATE CATEGORY

        category_id = request.POST.get(
            'category_id'
        )

        name = request.POST.get(
            'name'
        )

        if category_id:

            category = get_object_or_404(

                Category,

                id=category_id

            )

            category.name = name

            category.save()

            clear_blog_cache()

            messages.success(

                request,

                'Category updated successfully.'

            )

        else:

            Category.objects.create(
                name=name
            )

            clear_blog_cache()

            messages.success(

                request,

                'Category created successfully.'

            )

        return redirect(
            'manage_categories'
        )

    # =====================================
    # SEARCH
    # =====================================

    search = request.GET.get(
        'search'
    )

    categories = Category.objects.all()

    if search:

        categories = categories.filter(

            name__icontains=search

        )

    context = {

        'categories': categories,

        'edit_category': edit_category,

        'search_query': search,

    }

    return render(

        request,

        'blog/manage_categories.html',

        context

    )


# =========================================
# MANAGE TAGS
# =========================================


@staff_member_required
@login_required
def manage_tags(request):

    if not request.user.is_superuser:

        return redirect(
            'dashboard'
        )

    # =====================================
    # EDIT TAG
    # =====================================

    edit_id = request.GET.get(
        'edit'
    )

    edit_tag = None

    if edit_id:

        edit_tag = get_object_or_404(

            Tag,

            id=edit_id

        )

    # =====================================
    # POST ACTIONS
    # =====================================

    if request.method == 'POST':

        # DELETE TAG

        delete_id = request.POST.get(
            'delete_tag_id'
        )

        if delete_id:

            tag = get_object_or_404(

                Tag,

                id=delete_id

            )

            tag.delete()

            clear_blog_cache()

            messages.success(

                request,

                'Tag deleted successfully.'

            )

            return redirect(
                'manage_tags'
            )

        # CREATE / UPDATE TAG

        tag_id = request.POST.get(
            'tag_id'
        )

        name = request.POST.get(
            'name'
        )

        if tag_id:

            tag = get_object_or_404(

                Tag,

                id=tag_id

            )

            tag.name = name

            tag.save()

            messages.success(

                request,

                'Tag updated successfully.'

            )

        else:

            Tag.objects.create(
                name=name
            )

            messages.success(

                request,

                'Tag created successfully.'

            )

        return redirect(
            'manage_tags'
        )

    # =====================================
    # SEARCH
    # =====================================

    search = request.GET.get(
        'search'
    )

    tags = Tag.objects.all()

    if search:

        tags = tags.filter(

            name__icontains=search

        )

    context = {

        'tags': tags,

        'edit_tag': edit_tag,

        'search_query': search,

    }

    return render(

        request,

        'blog/manage_tags.html',

        context

    )


# =========================================
# MANAGE COMMENTS
# =========================================


@staff_member_required
@login_required
def manage_comments(request):

    if not request.user.is_superuser:

        return redirect(
            'dashboard'
        )

    # =====================================
    # EDIT COMMENT
    # =====================================

    edit_id = request.GET.get(
        'edit'
    )

    edit_comment = None

    if edit_id:

        edit_comment = get_object_or_404(

            Comment,

            id=edit_id

        )

    # =====================================
    # HANDLE POST ACTIONS
    # =====================================

    if request.method == 'POST':

        # DELETE COMMENT

        delete_comment_id = request.POST.get(
            'delete_comment_id'
        )

        if delete_comment_id:

            comment = get_object_or_404(

                Comment,

                id=delete_comment_id

            )

            comment.delete()

            clear_blog_cache()

            messages.success(

                request,

                'Comment deleted successfully.'

            )

            return redirect(
                'manage_comments'
            )

        # UPDATE COMMENT

        comment_id = request.POST.get(
            'comment_id'
        )

        if comment_id:

            content = request.POST.get(
                'content'
            )

            rating = request.POST.get(
                'rating'
            )

            comment = get_object_or_404(

                Comment,

                id=comment_id

            )

            comment.content = content

            comment.rating = rating

            comment.save()

            clear_blog_cache()

            messages.success(

                request,

                'Comment updated successfully.'

            )

            return redirect(
                'manage_comments'
            )

    # =====================================
    # SEARCH
    # =====================================

    search = request.GET.get(
        'search'
    )

    comments = Comment.objects.select_related(

        'author',
        'post'

    ).all().order_by(
        '-created_at'
    )

    if search:

        comments = comments.filter(

            Q(content__icontains=search) |

            Q(author__username__icontains=search) |

            Q(post__title__icontains=search)

        )

    # =====================================
    # PAGINATION
    # =====================================

    paginator = Paginator(

        comments,
        10

    )

    page_number = request.GET.get(
        'page'
    )

    page_obj = paginator.get_page(
        page_number
    )

    context = {

        'comments': page_obj,

        'page_obj': page_obj,

        'edit_comment': edit_comment,

        'search_query': search,

        'results_count': paginator.count,

    }

    return render(

        request,

        'blog/manage_comments.html',

        context

    )
# =========================================
# NOTIFICATIONS
# =========================================

@login_required
def notifications(request):

    # =====================================
    # ROLE PROTECTION
    # =====================================

    if request.user.role not in [

        'admin',
        'author'

    ]:

        messages.error(

            request,
            'You are not allowed to access notifications.'

        )

        return redirect(

            'blog_list'

        )

    # =====================================
    # GET ALL NOTIFICATIONS
    # =====================================

    notifications = request.user.notifications.select_related(

        'sender',
        'post'

    ).order_by(

        '-created_at'

    )

    # =====================================
    # UNREAD COUNT
    # =====================================

    unread_count = notifications.filter(

        is_read=False

    ).count()

    # =====================================
    # MARK AS READ AFTER OPENING PAGE
    # =====================================

    notifications.filter(

        is_read=False

    ).update(

        is_read=True

    )

    context = {

        'notifications': notifications,
        'unread_count': unread_count,

    }

    return render(

        request,
        'blog/notifications.html',
        context

    )


# =========================================
# LIKED POSTS
# =========================================

@login_required
def liked_posts(request):

    posts = BlogPost.objects.filter(
        likes=request.user
    ).optimized()

    context = {

        'posts': posts,

    }

    return render(

        request,

        'blog/liked_posts.html',

        context

    )


# =========================================
# COMMENTED POSTS
# =========================================

@login_required
def commented_posts(request):

    posts = BlogPost.objects.filter(

        comments__author=request.user

    ).distinct().optimized()

    context = {

        'posts': posts,

    }

    return render(

        request,

        'blog/commented_posts.html',

        context

    )


# =========================================
# MANAGE USERS
# =========================================

@staff_member_required
@login_required
def manage_users(request):

    # ADMIN ONLY

    if not request.user.is_superuser:

        return redirect(
            'dashboard'
        )

    users = CustomUser.objects.all().order_by(
        '-date_joined'
    )

    context = {

        'users': users,

    }

    return render(

        request,

        'blog/manage_users.html',

        context

    )