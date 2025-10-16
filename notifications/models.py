from django.db import models


class Notification(models.Model):
    """
    Modelo para armazenar histórico de notificações enviadas.
    """
    STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('sent', 'Enviado'),
        ('failed', 'Falhou'),
    ]
    
    recipient_email = models.EmailField(
        verbose_name='Email do Destinatário',
        help_text='Email para o qual a notificação será enviada'
    )
    subject = models.CharField(
        max_length=200,
        verbose_name='Assunto',
        help_text='Assunto do email'
    )
    message = models.TextField(
        verbose_name='Mensagem',
        help_text='Corpo da mensagem do email'
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Status'
    )
    error_message = models.TextField(
        blank=True,
        null=True,
        verbose_name='Mensagem de Erro',
        help_text='Detalhes do erro, caso o envio falhe'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Data de Criação'
    )
    sent_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Data de Envio'
    )
    
    class Meta:
        verbose_name = 'Notificação'
        verbose_name_plural = 'Notificações'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.subject} - {self.recipient_email} ({self.status})"
