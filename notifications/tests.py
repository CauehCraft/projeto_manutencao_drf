from django.test import TestCase
from django.core import mail
from rest_framework.test import APITestCase
from rest_framework import status
from notifications.models import Notification
from notifications.services import EmailService
import json


class NotificationModelTest(TestCase):
    """Testes para o modelo Notification"""
    
    def setUp(self):
        self.notification = Notification.objects.create(
            recipient_email='teste@example.com',
            subject='Teste',
            message='Mensagem de teste'
        )
    
    def test_notification_creation(self):
        """Testa a criação de uma notificação"""
        self.assertEqual(self.notification.recipient_email, 'teste@example.com')
        self.assertEqual(self.notification.subject, 'Teste')
        self.assertEqual(self.notification.status, 'pending')
    
    def test_notification_str(self):
        """Testa a representação em string"""
        expected = 'Teste - teste@example.com (pending)'
        self.assertEqual(str(self.notification), expected)


class EmailServiceTest(TestCase):
    """Testes para o serviço de email"""
    
    def test_send_email_success(self):
        """Testa envio de email com sucesso"""
        success, notification, error = EmailService.send_notification(
            recipient_email='teste@example.com',
            subject='Teste de Email',
            message='Conteúdo do teste'
        )
        
        self.assertTrue(success)
        self.assertIsNotNone(notification)
        self.assertIsNone(error)
        self.assertEqual(notification.status, 'sent')
        self.assertIsNotNone(notification.sent_at)
        
        # Verifica se o email foi "enviado" (no backend de console)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Teste de Email')
    
    def test_prevent_duplicate_notification(self):
        """Testa prevenção de notificações duplicadas"""
        # Envia a primeira notificação
        success1, notification1, error1 = EmailService.send_notification(
            recipient_email='teste@example.com',
            subject='Notificação Única',
            message='Esta notificação não deve ser duplicada'
        )
        
        self.assertTrue(success1)
        self.assertEqual(notification1.status, 'sent')
        
        # Tenta enviar a mesma notificação novamente
        success2, notification2, error2 = EmailService.send_notification(
            recipient_email='teste@example.com',
            subject='Notificação Única',
            message='Esta notificação não deve ser duplicada'
        )
        
        self.assertTrue(success2)
        self.assertIsNone(error2)
        # Deve retornar a mesma notificação (mesma ID)
        self.assertEqual(notification1.id, notification2.id)
        
        # Verifica que apenas 1 notificação foi criada no banco
        self.assertEqual(Notification.objects.count(), 1)
        
        # Verifica que apenas 1 email foi enviado
        self.assertEqual(len(mail.outbox), 1)
    
    def test_allow_different_notifications(self):
        """Testa que notificações diferentes são enviadas normalmente"""
        # Envia primeira notificação
        success1, notification1, error1 = EmailService.send_notification(
            recipient_email='teste@example.com',
            subject='Primeira Notificação',
            message='Primeira mensagem'
        )
        
        # Envia segunda notificação com conteúdo diferente
        success2, notification2, error2 = EmailService.send_notification(
            recipient_email='teste@example.com',
            subject='Segunda Notificação',
            message='Segunda mensagem'
        )
        
        self.assertTrue(success1)
        self.assertTrue(success2)
        
        # Devem ser notificações diferentes
        self.assertNotEqual(notification1.id, notification2.id)
        
        # Verifica que 2 notificações foram criadas
        self.assertEqual(Notification.objects.count(), 2)
        
        # Verifica que 2 emails foram enviados
        self.assertEqual(len(mail.outbox), 2)
    
    def test_allow_same_message_different_recipients(self):
        """Testa que a mesma mensagem pode ser enviada para destinatários diferentes"""
        # Envia para primeiro destinatário
        success1, notification1, error1 = EmailService.send_notification(
            recipient_email='usuario1@example.com',
            subject='Notificação',
            message='Mesma mensagem'
        )
        
        # Envia para segundo destinatário
        success2, notification2, error2 = EmailService.send_notification(
            recipient_email='usuario2@example.com',
            subject='Notificação',
            message='Mesma mensagem'
        )
        
        self.assertTrue(success1)
        self.assertTrue(success2)
        
        # Devem ser notificações diferentes
        self.assertNotEqual(notification1.id, notification2.id)
        
        # Verifica que 2 notificações foram criadas
        self.assertEqual(Notification.objects.count(), 2)
        
        # Verifica que 2 emails foram enviados
        self.assertEqual(len(mail.outbox), 2)


class NotificationAPITest(APITestCase):
    """Testes para a API de notificações"""
    
    def test_send_notification_success(self):
        """Testa endpoint de envio de notificação"""
        data = {
            'recipient_email': 'api_teste@example.com',
            'subject': 'Teste via API',
            'message': 'Mensagem de teste via API'
        }
        
        response = self.client.post('/api/notifications/send/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertIn('notification', response.data)
        
        # Verifica se foi criado no banco
        self.assertEqual(Notification.objects.count(), 1)
    
    def test_send_notification_invalid_email(self):
        """Testa envio com email inválido"""
        data = {
            'recipient_email': 'email-invalido',
            'subject': 'Teste',
            'message': 'Mensagem'
        }
        
        response = self.client.post('/api/notifications/send/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        self.assertIn('errors', response.data)
    
    def test_send_notification_missing_fields(self):
        """Testa envio com campos faltando"""
        data = {
            'recipient_email': 'teste@example.com'
        }
        
        response = self.client.post('/api/notifications/send/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
    
    def test_list_notifications(self):
        """Testa listagem de notificações"""
        # Cria algumas notificações
        Notification.objects.create(
            recipient_email='teste1@example.com',
            subject='Teste 1',
            message='Mensagem 1'
        )
        Notification.objects.create(
            recipient_email='teste2@example.com',
            subject='Teste 2',
            message='Mensagem 2'
        )
        
        response = self.client.get('/api/notifications/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
    
    def test_filter_notifications_by_status(self):
        """Testa filtro por status"""
        # Cria notificações com status diferentes
        Notification.objects.create(
            recipient_email='teste1@example.com',
            subject='Teste 1',
            message='Mensagem 1',
            status='sent'
        )
        Notification.objects.create(
            recipient_email='teste2@example.com',
            subject='Teste 2',
            message='Mensagem 2',
            status='pending'
        )
        
        response = self.client.get('/api/notifications/?status=sent')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['status'], 'sent')
    
    def test_notification_detail(self):
        """Testa detalhes de uma notificação"""
        notification = Notification.objects.create(
            recipient_email='teste@example.com',
            subject='Teste',
            message='Mensagem'
        )
        
        response = self.client.get(f'/api/notifications/{notification.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], notification.id)
    
    def test_statistics(self):
        """Testa endpoint de estatísticas"""
        # Cria notificações com diferentes status
        Notification.objects.create(
            recipient_email='teste1@example.com',
            subject='Teste 1',
            message='Mensagem 1',
            status='sent'
        )
        Notification.objects.create(
            recipient_email='teste2@example.com',
            subject='Teste 2',
            message='Mensagem 2',
            status='failed'
        )
        Notification.objects.create(
            recipient_email='teste3@example.com',
            subject='Teste 3',
            message='Mensagem 3',
            status='pending'
        )
        
        response = self.client.get('/api/notifications/statistics/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total'], 3)
        self.assertEqual(response.data['sent'], 1)
        self.assertEqual(response.data['failed'], 1)
        self.assertEqual(response.data['pending'], 1)
    
    def test_delete_notification(self):
        """Testa deleção de notificação"""
        notification = Notification.objects.create(
            recipient_email='teste@example.com',
            subject='Teste',
            message='Mensagem'
        )
        
        response = self.client.delete(f'/api/notifications/{notification.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Notification.objects.count(), 0)


class NotificationIntegrationTest(APITestCase):
    """Testes de integração completos da API de notificações"""
    
    def test_complete_notification_workflow(self):
        """Testa o fluxo completo: envio -> listagem -> detalhes"""
        # 1. Enviar notificação
        data = {
            'recipient_email': 'teste@example.com',
            'subject': 'Teste de Notificação via API',
            'message': 'Esta é uma mensagem de teste enviada através da API REST'
        }
        
        response = self.client.post('/api/notifications/send/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        
        notification_id = response.data['notification']['id']
        
        # 2. Listar notificações
        response = self.client.get('/api/notifications/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(response.data['count'], 1)
        
        # 3. Obter detalhes
        response = self.client.get(f'/api/notifications/{notification_id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], notification_id)
        self.assertEqual(response.data['recipient_email'], 'teste@example.com')
    
    def test_send_invalid_notification(self):
        """Testa validação de dados inválidos"""
        data = {
            'recipient_email': 'email-invalido',
            'subject': '',
            'message': ''
        }
        
        response = self.client.post('/api/notifications/send/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        self.assertIn('errors', response.data)
    
    def test_send_multiple_notifications(self):
        """Testa envio de múltiplas notificações"""
        emails = [
            {
                'recipient_email': 'usuario1@example.com',
                'subject': 'Bem-vindo!',
                'message': 'Bem-vindo ao nosso sistema!'
            },
            {
                'recipient_email': 'usuario2@example.com',
                'subject': 'Confirmação de Cadastro',
                'message': 'Seu cadastro foi confirmado com sucesso.'
            },
            {
                'recipient_email': 'usuario3@example.com',
                'subject': 'Atualização de Sistema',
                'message': 'O sistema será atualizado amanhã às 2h.'
            }
        ]
        
        successful_sends = 0
        for email_data in emails:
            response = self.client.post('/api/notifications/send/', email_data, format='json')
            if response.status_code == status.HTTP_201_CREATED:
                successful_sends += 1
        
        self.assertEqual(successful_sends, 3)
        self.assertEqual(Notification.objects.count(), 3)
    
    def test_filter_notifications_by_status(self):
        """Testa filtro de notificações por status"""
        # Criar notificações com status 'sent'
        self.client.post('/api/notifications/send/', {
            'recipient_email': 'sent@example.com',
            'subject': 'Email Sent',
            'message': 'Message sent'
        }, format='json')
        
        # Filtrar por status
        response = self.client.get('/api/notifications/?status=sent')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar que todos os resultados têm o status correto
        for notification in response.data['results']:
            self.assertEqual(notification['status'], 'sent')
    
    def test_statistics_endpoint(self):
        """Testa endpoint de estatísticas"""
        # Criar algumas notificações
        for i in range(3):
            self.client.post('/api/notifications/send/', {
                'recipient_email': f'user{i}@example.com',
                'subject': f'Test {i}',
                'message': f'Message {i}'
            }, format='json')
        
        # Obter estatísticas
        response = self.client.get('/api/notifications/statistics/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total', response.data)
        self.assertIn('sent', response.data)
        self.assertIn('pending', response.data)
        self.assertIn('failed', response.data)
        self.assertEqual(response.data['total'], 3)
    
    def test_notification_not_found(self):
        """Testa acesso a notificação inexistente"""
        response = self.client.get('/api/notifications/99999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_email_actually_sent(self):
        """Testa se o email é realmente enviado (para console backend)"""
        data = {
            'recipient_email': 'test@example.com',
            'subject': 'Test Email',
            'message': 'Test message content'
        }
        
        # Limpar mailbox
        mail.outbox = []
        
        response = self.client.post('/api/notifications/send/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verificar se o email foi enviado
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Test Email')
        self.assertEqual(mail.outbox[0].to, ['test@example.com'])
    
    def test_api_prevent_duplicate_notifications(self):
        """Testa que a API previne o envio de notificações duplicadas"""
        data = {
            'recipient_email': 'duplicate@example.com',
            'subject': 'Test Duplicate',
            'message': 'This should not be duplicated'
        }
        
        # Limpar mailbox
        mail.outbox = []
        
        # Primeiro envio
        response1 = self.client.post('/api/notifications/send/', data, format='json')
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response1.data['success'])
        notification_id_1 = response1.data['notification']['id']
        
        # Segundo envio (duplicado)
        response2 = self.client.post('/api/notifications/send/', data, format='json')
        self.assertEqual(response2.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response2.data['success'])
        notification_id_2 = response2.data['notification']['id']
        
        # Deve retornar a mesma notificação
        self.assertEqual(notification_id_1, notification_id_2)
        
        # Apenas 1 notificação no banco
        self.assertEqual(Notification.objects.count(), 1)
        
        # Apenas 1 email enviado
        self.assertEqual(len(mail.outbox), 1)
