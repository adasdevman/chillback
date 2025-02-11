from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from core.models.notification import Notification
from core.serializers.notification import NotificationSerializer

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def notifications_list(request):
    """
    Récupère la liste des notifications de l'utilisateur connecté
    """
    notifications = Notification.objects.filter(user=request.user)
    serializer = NotificationSerializer(notifications, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_notification_read(request, notification_id):
    """
    Marque une notification comme lue
    """
    try:
        notification = Notification.objects.get(
            id=notification_id,
            user=request.user
        )
        notification.mark_as_read()
        return Response({'status': 'success'})
    except Notification.DoesNotExist:
        return Response(
            {'error': 'Notification non trouvée'},
            status=status.HTTP_404_NOT_FOUND
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_all_read(request):
    """
    Marque toutes les notifications de l'utilisateur comme lues
    """
    Notification.objects.filter(user=request.user, read=False).update(read=True)
    return Response({'status': 'success'})

def create_notification(user, type, title, message, data=None):
    """
    Fonction utilitaire pour créer une nouvelle notification
    """
    return Notification.objects.create(
        user=user,
        type=type,
        title=title,
        message=message,
        data=data
    ) 