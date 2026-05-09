import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from .models import Notification
from .serializers import NotificationSerializer


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if self.scope['user'] == AnonymousUser():
            await self.close()
            return

        self.group_name = f'user_{self.scope["user"].id}'
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

    @database_sync_to_async
    def _get_notification(self, notification_id):
        return Notification.objects.filter(id=notification_id).first()

    # 发送通知更新
    async def send_notification_update(self, notification_id):
        notification = await self._get_notification(notification_id)
        if notification:
            serializer = NotificationSerializer(notification)
            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'notification.updated',
                    'notification': serializer.data
                }
            )

    # 发送通知删除
    async def send_notification_deletion(self, notification_id):
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'notification.deleted',
                'notification_id': notification_id
            }
        )

    # 处理前端事件
    async def receive(self, text_data):
        data = json.loads(text_data)
        if data.get('action') == 'mark_as_read':
            await self._mark_as_read(data['notification_id'])

    @database_sync_to_async
    def _mark_as_read(self, notification_id):
        notification = Notification.objects.filter(
            id=notification_id, is_read=False
        ).first()
        if notification:
            notification.is_read = True
            notification.save()
            self.send_notification_update(notification_id)

    # WebSocket消息处理
    async def notification_updated(self, event):
        await self.send(text_data=json.dumps(event['notification']))

    async def notification_deleted(self, event):
        await self.send(text_data=json.dumps({
            'type': 'delete',
            'id': event['notification_id']
        }))