from django.urls import path
from django.contrib.auth import views as auth_views

from django.contrib.auth.views import (
    LoginView,
    LogoutView
)

from .views import (
    signup_view,
    home,
    dashboard,
    profile_view,
    activate
)

from .forms import CustomAuthenticationForm


urlpatterns = [

    path(
        '',
        home,
        name='home'
    ),

    path(
        'signup/',
        signup_view,
        name='signup'
    ),

    path(
    'login/',
    LoginView.as_view(

        template_name='accounts/login.html',

        authentication_form=CustomAuthenticationForm,

        redirect_authenticated_user=True,

        next_page='/'

    ),
    name='login'
),

    path(
        'logout/',
        LogoutView.as_view(),
        name='logout'
    ),

    path(
        'dashboard/',
        dashboard,
        name='dashboard'
    ),

    path(
        'profile/',
        profile_view,
        name='profile'
    ),

    path(
        'activate/<uidb64>/<token>/',
        activate,
        name='activate'
    ),

    path(
    'password-reset/',
    auth_views.PasswordResetView.as_view(
        template_name='accounts/password_reset.html'
    ),
    name='password_reset'
),

path(
    'password-reset/done/',
    auth_views.PasswordResetDoneView.as_view(
        template_name='accounts/password_reset_done.html'
    ),
    name='password_reset_done'
),

path(
    'reset/<uidb64>/<token>/',
    auth_views.PasswordResetConfirmView.as_view(
        template_name='accounts/password_reset_confirm.html'
    ),
    name='password_reset_confirm'
),

path(
    'reset/done/',
    auth_views.PasswordResetCompleteView.as_view(
        template_name='accounts/password_reset_complete.html'
    ),
    name='password_reset_complete'
),
]