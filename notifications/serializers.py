from rest_framework import serializers
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    """
    Serializer para o modelo Notification.
    Usado para envio e listagem de notificações.
    """
    
    class Meta:
        model = Notification
        fields = [
            'id',
            'recipient_email',
            'subject',
            'message',
            'status',
            'error_message',
            'created_at',
            'sent_at'
        ]
        read_only_fields = ['id', 'status', 'error_message', 'created_at', 'sent_at']


class SendNotificationSerializer(serializers.Serializer):
    """
    Serializer específico para o endpoint de envio de notificações.
    Valida os dados de entrada antes do envio.
    """
    recipient_email = serializers.EmailField(
        help_text='Email do destinatário',
        required=True
    )
    subject = serializers.CharField(
        max_length=200,
        help_text='Assunto do email',
        required=True
    )
    message = serializers.CharField(
        help_text='Corpo da mensagem do email',
        required=True
    )
    
    def validate_recipient_email(self, value):
        """
        Validação customizada para o email do destinatário.
        """
        if not value:
            raise serializers.ValidationError("O email do destinatário é obrigatório.")
        return value.lower()
    
    def validate_subject(self, value):
        """
        Validação customizada para o assunto.
        """
        if not value.strip():
            raise serializers.ValidationError("O assunto não pode estar vazio.")
        return value.strip()
    
    def validate_message(self, value):
        """
        Validação customizada para a mensagem.
        """
        if not value.strip():
            raise serializers.ValidationError("A mensagem não pode estar vazia.")
        return value.strip()
