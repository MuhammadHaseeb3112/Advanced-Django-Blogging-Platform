from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser


class CustomUserAdmin(UserAdmin):

    model = CustomUser

    fieldsets = UserAdmin.fieldsets + (

        (
            'Additional Info',
            {
                'fields': (

                    'bio',

                    'profile_image',

                    'role',

                    'email_verified',

                )
            }
        ),

    )

    add_fieldsets = UserAdmin.add_fieldsets + (

        (
            None,
            {
                'fields': (

                    'email',

                    'bio',

                    'profile_image',

                    'role',

                    'email_verified',

                ),
            },
        ),

    )

    list_display = (

        'username',

        'email',

        'role',

        'email_verified',

        'is_staff',

    )


admin.site.register(
    CustomUser,
    CustomUserAdmin
)