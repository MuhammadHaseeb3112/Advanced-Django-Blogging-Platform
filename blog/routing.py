from django.urls import path

from .consumers import (

    NotificationConsumer,
    BlogConsumer

)


websocket_urlpatterns = [

    path(

        'ws/notifications/',

        NotificationConsumer.as_asgi()

    ),

    path(

        'ws/blog/<int:blog_id>/',

        BlogConsumer.as_asgi()

    ),

]