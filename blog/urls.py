from django.urls import path

from . import views

urlpatterns = [


    # =========================================
    # BLOGS
    # =========================================

path(

    'blogs/',

    views.BlogListView.as_view(),

    name='blog_list'

),

path(

    'blogs/<slug:slug>/',

    views.BlogDetailView.as_view(),

    name='blog_detail'

),
    # =========================================
    # AJAX LIKE
    # =========================================

    path(
        'blogs/<slug:slug>/like/',
        views.like_post,
        name='like_post'
    ),

    # =========================================
    # AJAX BOOKMARK
    # =========================================

    path(
        'blogs/<slug:slug>/bookmark/',
        views.bookmark_post,
        name='bookmark_post'
    ),

    # =========================================
    # AJAX COMMENT
    # =========================================

    path(
        'blogs/<slug:slug>/comment/',
        views.add_comment,
        name='add_comment'
    ),

    # =========================================
    # DASHBOARD
    # =========================================

    path(
        'dashboard/',
        views.dashboard,
        name='dashboard'
    ),

path(
    'profile/',
    views.profile_view,
    name='profile'
),

    # =========================================
    # POSTS MANAGEMENT
    # =========================================

    path(
        'create-post/',
        views.create_post,
        name='create_post'
    ),

    path(
        'my-posts/',
        views.my_posts,
        name='my_posts'
    ),

    path(
        'update-post/<slug:slug>/',
        views.update_post,
        name='update_post'
    ),

    path(
        'delete-post/<slug:slug>/',
        views.delete_post,
        name='delete_post'
    ),

    # =========================================
    # USER ACTIVITY
    # =========================================

    path(
        'saved-posts/',
        views.saved_posts,
        name='saved_posts'
    ),

    path(
        'liked-posts/',
        views.liked_posts,
        name='liked_posts'
    ),

    path(
        'commented-posts/',
        views.commented_posts,
        name='commented_posts'
    ),

    # =========================================
    # ADMIN
    # =========================================

    path(
        'users/',
        views.manage_users,
        name='manage_users'
    ),

    path(
        'manage-comments/',
        views.manage_comments,
        name='manage_comments'
    ),

    path(
        'manage-categories/',
        views.manage_categories,
        name='manage_categories'
    ),

    path(
        'manage-tags/',
        views.manage_tags,
        name='manage_tags'
    ),

    # =========================================
    # NOTIFICATIONS
    # =========================================

    path(
        'notifications/',
        views.notifications,
        name='notifications'
    ),


    
]