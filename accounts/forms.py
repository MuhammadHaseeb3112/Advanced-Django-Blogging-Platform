from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.forms import ModelForm
from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):

    class Meta:
        model = CustomUser
        fields = ('username', 'email')


class CustomAuthenticationForm(AuthenticationForm):

    username = forms.EmailField()

    from django.forms import ModelForm


class UserUpdateForm(ModelForm):

    class Meta:
        model = CustomUser

        fields = [
            'username',
            'email',
            'bio',
            'profile_image',
        ]