from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from .models import Notification
from .serializers import NotificationSerializer, SendNotificationSerializer
from .services import EmailService


class NotificationViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciamento de notificações.
    
    Endpoints disponíveis:
    - GET /api/notifications/ - Lista todas as notificações
    - GET /api/notifications/{id}/ - Detalhes de uma notificação
    - POST /api/notifications/send/ - Envia uma nova notificação
    - DELETE /api/notifications/{id}/ - Remove uma notificação
    """
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [AllowAny]  # Em produção, considerar adicionar autenticacao
    
    def get_queryset(self):
        """
        Permite filtrar notificações por status via query parameter.
        Exemplo: /api/notifications/?status=sent
        """
        queryset = Notification.objects.all()
        status_filter = self.request.query_params.get('status', None)
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset
    
    @action(detail=False, methods=['post'], url_path='send')
    def send(self, request):
        """
        Endpoint customizado para envio de notificações.
        
        POST /api/notifications/send/
        Body: {
            "recipient_email": "usuario@example.com",
            "subject": "Título da notificação",
            "message": "Mensagem da notificação"
        }
        """
        serializer = SendNotificationSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                {
                    'success': False,
                    'errors': serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Extrai os dados validados
        validated_data = serializer.validated_data
        recipient_email = validated_data['recipient_email']
        subject = validated_data['subject']
        message = validated_data['message']
        
        # Envia o email usando o serviço
        success, notification, error_message = EmailService.send_notification(
            recipient_email=recipient_email,
            subject=subject,
            message=message
        )
        
        if success:
            return Response(
                {
                    'success': True,
                    'message': 'Notificação enviada com sucesso!',
                    'notification': NotificationSerializer(notification).data
                },
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                {
                    'success': False,
                    'message': 'Falha ao enviar notificação',
                    'error': error_message,
                    'notification': NotificationSerializer(notification).data
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'], url_path='statistics')
    def statistics(self, request):
        """
        Endpoint para obter estatísticas de notificações.
        
        GET /api/notifications/statistics/
        """
        total = Notification.objects.count()
        sent = Notification.objects.filter(status='sent').count()
        failed = Notification.objects.filter(status='failed').count()
        pending = Notification.objects.filter(status='pending').count()
        
        return Response({
            'total': total,
            'sent': sent,
            'failed': failed,
            'pending': pending,
            'success_rate': round((sent / total * 100) if total > 0 else 0, 2)
        })
