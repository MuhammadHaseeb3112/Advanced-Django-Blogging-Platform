from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class CustomUser(AbstractUser):

    class Roles(models.TextChoices):
        ADMIN = "admin", _("Admin")
        AUTHOR = "author", _("Author")
        USER = "user", _("User")

    email = models.EmailField(unique=True)

    bio = models.TextField(blank=True)

    profile_image = models.ImageField(
        upload_to='profiles/',
        blank=True,
        null=True
    )

    role = models.CharField(
        max_length=20,
        choices=Roles.choices,
        default=Roles.USER
    )

    email_verified = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email