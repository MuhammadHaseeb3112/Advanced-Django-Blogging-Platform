from django.db.models.signals import (

    pre_save,
    post_save,
    post_delete,
    m2m_changed

)

from django.dispatch import receiver

from django.utils.text import slugify

from django.core.cache import cache

from .models import (

    BlogPost,
    Comment,
    Notification,
    Category,
    Tag

)

# =========================================
# CACHE CLEAR FUNCTION
# =========================================

def clear_blog_cache():

    print(
        'CLEARING BLOG CACHE 🚀'
    )

    cache.clear()

# =========================================
# AUTO SLUG GENERATION
# =========================================

@receiver(pre_save, sender=BlogPost)
def create_blog_slug(sender, instance, *args, **kwargs):

    # =====================================
    # ONLY CREATE SLUG IF EMPTY
    # =====================================

    if not instance.slug:

        base_slug = slugify(
            instance.title
        )

        unique_slug = base_slug

        counter = 1

        # =================================
        # UNIQUE SLUG GENERATION
        # =================================

        while BlogPost.objects.filter(
            slug=unique_slug
        ).exists():

            unique_slug = f'{base_slug}-{counter}'

            counter += 1

        instance.slug = unique_slug

# =========================================
# BLOG CACHE INVALIDATION
# =========================================

@receiver(post_save, sender=BlogPost)
def clear_cache_on_blog_save(

    sender,

    instance,

    **kwargs

):

    clear_blog_cache()

# =========================================
# BLOG DELETE CACHE INVALIDATION
# =========================================

@receiver(post_delete, sender=BlogPost)
def clear_cache_on_blog_delete(

    sender,

    instance,

    **kwargs

):

    clear_blog_cache()

# =========================================
# CATEGORY CACHE INVALIDATION
# =========================================

@receiver(post_save, sender=Category)
def clear_cache_on_category_save(

    sender,

    instance,

    **kwargs

):

    clear_blog_cache()

# =========================================
# TAG CACHE INVALIDATION
# =========================================

@receiver(post_save, sender=Tag)
def clear_cache_on_tag_save(

    sender,

    instance,

    **kwargs

):

    clear_blog_cache()

# =========================================
# TAG RELATION CACHE INVALIDATION
# =========================================

@receiver(

    m2m_changed,

    sender=BlogPost.tags.through

)
def clear_cache_on_tags_change(

    sender,

    instance,

    **kwargs

):

    clear_blog_cache()

# =========================================
# LIKE NOTIFICATIONS
# =========================================

@receiver(m2m_changed, sender=BlogPost.likes.through)
def create_like_notification(

    sender,

    instance,

    action,

    pk_set,

    **kwargs

):

    # =====================================
    # AFTER USER LIKES POST
    # =====================================

    if action == 'post_add':

        clear_blog_cache()

        for user_id in pk_set:

            # =================================
            # PREVENT SELF NOTIFICATIONS
            # =================================

            if instance.author.id != user_id:

                # =============================
                # PREVENT DUPLICATE NOTIFICATION
                # =============================

                already_exists = Notification.objects.filter(

                    sender_id=user_id,

                    receiver=instance.author,

                    post=instance,

                    notification_type='like'

                ).exists()

                if not already_exists:

                    Notification.objects.create(

                        sender_id=user_id,

                        receiver=instance.author,

                        post=instance,

                        notification_type='like'

                    )

    # =====================================
    # REMOVE NOTIFICATION AFTER UNLIKE
    # =====================================

    if action == 'post_remove':

        clear_blog_cache()

        for user_id in pk_set:

            Notification.objects.filter(

                sender_id=user_id,

                receiver=instance.author,

                post=instance,

                notification_type='like'

            ).delete()
