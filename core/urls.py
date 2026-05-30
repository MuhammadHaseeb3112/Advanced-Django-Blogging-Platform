from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static
from .views import home



from drf_spectacular.views import (

    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,

)

from rest_framework import permissions

from drf_yasg.views import get_schema_view

from drf_yasg import openapi

schema_view = get_schema_view(

    openapi.Info(

        title="Django Blog API",

        default_version='v1',

        description="Advanced Django Blog API",

    ),

    public=True,

    permission_classes=[permissions.AllowAny],

)


urlpatterns = [

    path(
        'admin/',
        admin.site.urls
    ),

    # =====================================
    # HOME PAGE
    # =====================================

    path(
        '',
        home,
        name='home'
    ),

    # =====================================
    # ACCOUNTS
    # =====================================

    path(
        'accounts/',
        include('accounts.urls')
    ),

    # =====================================
    # API
    # =====================================



    path(
    "api/",
    include("api.urls")
),

   path(
    '',
    include('blog.urls')
),
   
    path(

        'swagger/',

        schema_view.with_ui(
            'swagger',
            cache_timeout=0
        ),

        name='schema-swagger-ui'

    ),


      # ==========================
    # API DOCUMENTATION
    # ==========================

    path(
        'api/schema/',
        SpectacularAPIView.as_view(),
        name='schema'
    ),

    path(
        'api/schema/swagger-ui/',
        SpectacularSwaggerView.as_view(
            url_name='schema'
        ),
        name='swagger-ui'
    ),

    path(
        'api/schema/redoc/',
        SpectacularRedocView.as_view(
            url_name='schema'
        ),
        name='redoc'
    ),

]

if settings.DEBUG:

    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )