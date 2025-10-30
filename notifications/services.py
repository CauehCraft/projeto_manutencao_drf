from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from .models import Notification
import logging

logger = logging.getLogger(__name__)


class EmailService:
    """
    Serviço responsável pelo envio de emails.
    """
    
    @staticmethod
    def send_notification(recipient_email, subject, message):
        """
        Envia uma notificação por email e registra no banco de dados.
        Verifica se já existe uma notificação idêntica enviada com sucesso
        para evitar duplicatas.
        
        Args:
            recipient_email (str): Email do destinatário
            subject (str): Assunto do email
            message (str): Corpo da mensagem
            
        Returns:
            tuple: (success, notification_instance, error_message)
        """
        # Verifica se já existe uma notificação idêntica enviada com sucesso
        existing_notification = Notification.objects.filter(
            recipient_email=recipient_email,
            subject=subject,
            message=message,
            status='sent'
        ).first()
        
        if existing_notification:
            logger.info(
                f"Notificação duplicada detectada para {recipient_email}. "
                f"Retornando notificação existente (ID: {existing_notification.id})"
            )
            return True, existing_notification, None
        
        # Cria o registro da notificação no banco
        notification = Notification.objects.create(
            recipient_email=recipient_email,
            subject=subject,
            message=message,
            status='pending'
        )
        
        try:
            # Tenta enviar o email
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient_email],
                fail_silently=False,
            )
            
            # Atualiza o status da notificação para 'sent'
            notification.status = 'sent'
            notification.sent_at = timezone.now()
            notification.save()
            
            logger.info(f"Email enviado com sucesso para {recipient_email}")
            return True, notification, None
            
        except Exception as e:
            # Em caso de erro, atualiza o status para 'failed'
            error_message = str(e)
            notification.status = 'failed'
            notification.error_message = error_message
            notification.save()
            
            logger.error(f"Erro ao enviar email para {recipient_email}: {error_message}")
            return False, notification, error_message
