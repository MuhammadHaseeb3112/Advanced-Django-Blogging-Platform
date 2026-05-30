import json

from channels.generic.websocket import AsyncWebsocketConsumer


class NotificationConsumer(

    AsyncWebsocketConsumer

):

    async def connect(self):

        self.user = self.scope['user']

        if self.user.is_anonymous:

            await self.close()

        else:

            self.group_name = f'user_{self.user.id}'

            print(f'USER CONNECTED: {self.user}')
            print(f'GROUP: {self.group_name}')

            await self.channel_layer.group_add(

                self.group_name,
                self.channel_name

            )

            await self.accept()


    async def disconnect(self, close_code):

        print('DISCONNECTED')

        if not self.user.is_anonymous:

            await self.channel_layer.group_discard(

                self.group_name,
                self.channel_name

            )

    async def send_notification(self, event):

        print('WEBSOCKET EVENT RECEIVED 🚀')

        await self.send(

            text_data=json.dumps({

                'message': event['message'],
                'unread_count': event['unread_count'],

            })

        )



class BlogConsumer(

    AsyncWebsocketConsumer

):

    async def connect(self):

        self.blog_id = (

            self.scope[
                'url_route'
            ]['kwargs']['blog_id']

        )

        self.blog_group_name = (

            f'blog_{self.blog_id}'

        )

        print(
            f'BLOG GROUP: '
            f'{self.blog_group_name}'
        )

        await self.channel_layer.group_add(

            self.blog_group_name,

            self.channel_name

        )

        await self.accept()


    async def disconnect(self, close_code):

        await self.channel_layer.group_discard(

            self.blog_group_name,

            self.channel_name

        )


    async def like_update(self, event):

        await self.send(

            text_data=json.dumps({

                'type': 'like_update',

                'likes_count': (

                    event['likes_count']

                ),

            })

        )


    async def comment_update(self, event):

        await self.send(

            text_data=json.dumps({

                'type': 'comment_update',

                'comments_count': (
                    event['comments_count']
                ),

                'comment_html': (
                    event.get('comment_html', '')
                ),

            })

        )


    async def bookmark_update(self, event):

        await self.send(

            text_data=json.dumps({

                'type': 'bookmark_update',

                'bookmarks_count': (

                    event['bookmarks_count']

                ),

            })

        )
    