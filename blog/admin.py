from django.contrib import admin

from .models import (

    BlogPost,
    Comment,
    Category,
    Tag,
    Notification

)


# =========================================
# COMMENT INLINE
# =========================================

class CommentInline(admin.TabularInline):

    model = Comment

    extra = 0

    readonly_fields = (

        'author',
        'content',
        'rating',
        'created_at'

    )


# =========================================
# BLOG POST ADMIN
# =========================================

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):

    list_display = (


    'id', 
    'title',
    'author',
    'category',
    'status',
    'publish_at',
    'total_likes',
    'created_at',
    

)

    list_filter = (

        'status',
        'category',
        'publish_at',
        'created_at'

    )

    search_fields = (

        'title',
        'content',
        'author__email'

    )

    prepopulated_fields = {

        'slug': ('title',)

    }

    readonly_fields = (

        'created_at',
        'updated_at'

    )

    ordering = (

        '-created_at',

    )

    filter_horizontal = (

        'tags',
        'likes',
        'bookmarks'

    )

    inlines = [

        CommentInline

    ]

    list_per_page = 20

    # =====================================
    # TOTAL LIKES
    # =====================================

    def total_likes(self, obj):

        return obj.likes.count()

    total_likes.short_description = 'Likes'


# =========================================
# COMMENT ADMIN
# =========================================

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):

    list_display = (

        'author',
        'post',
        'rating',
        'created_at'

    )

    list_filter = (

        'rating',
        'created_at'

    )

    search_fields = (

        'author__email',
        'content',
        'post__title'

    )

    readonly_fields = (

        'created_at',
        'updated_at'

    )

    ordering = (

        '-created_at',

    )

    list_per_page = 20


# =========================================
# CATEGORY ADMIN
# =========================================

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):

    list_display = (

        'name',
        'slug'

    )

    search_fields = (

        'name',

    )

    prepopulated_fields = {

        'slug': ('name',)

    }


# =========================================
# TAG ADMIN
# =========================================

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):

    list_display = (

        'name',
        'slug'

    )

    search_fields = (

        'name',

    )

    prepopulated_fields = {

        'slug': ('name',)

    }


# =========================================
# NOTIFICATION ADMIN
# =========================================

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):

    list_display = (


        'id',
        'sender',
        'receiver',
        'notification_type',
        'is_read',
        'created_at'

    )

    list_filter = (

        'notification_type',
        'is_read',
        'created_at'

    )

    search_fields = (

        'sender__email',
        'receiver__email',
        'post__title'

    )

    readonly_fields = (

        'created_at',

    )

    ordering = (

        '-created_at',

    )

    list_per_page = 20