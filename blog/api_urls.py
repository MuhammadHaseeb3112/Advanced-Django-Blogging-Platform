from rest_framework.routers import (
    DefaultRouter
)

from .api_views import (

    BlogPostViewSet,
    CommentViewSet,
    CategoryViewSet,
    TagViewSet,
)



router = DefaultRouter()

router.register(
    'posts',
    BlogPostViewSet
)

router.register(
    'comments',
    CommentViewSet
)

router.register(
    'categories',
    CategoryViewSet
)
router.register(
    'tags',
    TagViewSet
)


urlpatterns = router.urls
