from rest_framework import serializers
from ..models.notification import Notification

class NotificationSerializer(serializers.ModelSerializer):
    createdAt = serializers.DateTimeField(source='created', read_only=True)
    
    class Meta:
        model = Notification
        fields = [
            'id',
            'type',
            'title',
            'message',
            'read',
            'data',
            'createdAt'
        ]
        read_only_fields = ['id', 'createdAt'] 