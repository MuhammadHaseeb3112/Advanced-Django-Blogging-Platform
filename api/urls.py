from django.urls import path, include


from rest_framework.routers import DefaultRouter

from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

from api.views.auth_views import (
    RegisterAPIView,
    LogoutAPIView,
    CustomTokenObtainPairView,
)

from api.views.user_views import (

    UserAPIView,
    AdminOnlyAPIView,
    AuthorOnlyAPIView,
    ProfileView,
    ProfileUpdateAPIView,
    ChangePasswordAPIView,

)
from api.views.blog_views import (

    BlogPostViewSet,
    CommentViewSet,
    CategoryViewSet,
    TagViewSet,
    NotificationViewSet,
    AuthorProfileAPIView,


)

from api.views.dashboard_views import (

    DashboardAPIView,
    MyPostsAPIView,
    DraftPostsAPIView,
    PublishedPostsAPIView,

    BookmarkedPostsAPIView,
    LikedPostsAPIView,
    AnalyticsAPIView,
)


from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)


# =========================================
# ROUTER
# =========================================

router = DefaultRouter()

router.register(
    r'blogs',
    BlogPostViewSet,
    basename='blogs'
)

router.register(
    r'comments',
    CommentViewSet,
    basename='comments'
)

router.register(
    r'categories',
    CategoryViewSet,
    basename='categories'
)

router.register(
    r'tags',
    TagViewSet,
    basename='tags'
)

router.register(
    r'notifications',
    NotificationViewSet,
    basename='notifications'
)

# =========================================
# URLS
# =========================================

urlpatterns = [

    # =====================================
    # AUTH
    # =====================================

    path(
        'token/',
        CustomTokenObtainPairView.as_view(),
        name='token_obtain_pair'
    ),

    path(
        'token/refresh/',
        TokenRefreshView.as_view(),
        name='token_refresh'
    ),

    path(
        'register/',
        RegisterAPIView.as_view(),
        name='register_api'
    ),

    path(
        'logout/',
        LogoutAPIView.as_view(),
        name='logout_api'
    ),

    # =====================================
    # USER
    # =====================================

    path(
        'user/',
        UserAPIView.as_view(),
        name='user_api'
    ),

    path(
        'profile/',
        ProfileView.as_view(),
        name='profile'
    ),

    path(
    'profile/update/',
    ProfileUpdateAPIView.as_view(),
    name='profile_update'
),

    path('change-password/', ChangePasswordAPIView.as_view(), name='change-password'),

    # =====================================
    # ROLE BASED
    # =====================================

    path(
        'admin-only/',
        AdminOnlyAPIView.as_view(),
        name='admin_only'
    ),

    path(
        'author-only/',
        AuthorOnlyAPIView.as_view(),
        name='author_only'
    ),


   # =====================================
    # DASHBOARD
    # =====================================

    path(
    'dashboard/',
    DashboardAPIView.as_view(),
    name='dashboard_api'
    ),

    path(
    'my-posts/',
    MyPostsAPIView.as_view(),
    name='my_posts_api'
    ),

    path(
    'drafts/',
    DraftPostsAPIView.as_view(),
    name='draft_posts_api'
    ),

    path(
    'published/',
    PublishedPostsAPIView.as_view(),
    name='published_posts_api'  
    ),


    path(
    'bookmarks/',
    BookmarkedPostsAPIView.as_view(),
    name='bookmarked_posts_api'
    ),

    path(
    'liked-posts/',
    LikedPostsAPIView.as_view(),
    name='liked_posts_api'
    ),

    path(
    'analytics/',
    AnalyticsAPIView.as_view(),
    name='analytics_api'
    ),


    path(
    'authors/<str:username>/',
    AuthorProfileAPIView.as_view(),
    name='author_profile_api'
),

path(
    "schema/",
    SpectacularAPIView.as_view(),
    name="schema"
),

path(
    "docs/",
    SpectacularSwaggerView.as_view(url_name="schema"),
    name="swagger-ui"
),

path(
    "redoc/",
    SpectacularRedocView.as_view(url_name="schema"),
    name="redoc"
),

    # =====================================
    # ROUTER URLS
    # =====================================

    path(
        '',
        include(router.urls)
    ),



]