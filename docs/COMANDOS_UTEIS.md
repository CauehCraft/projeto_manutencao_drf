#  Comandos Úteis - Sistema de Notificações

Este arquivo contém comandos úteis para desenvolvimento e manutenção do sistema.

---

##  Instalação e Configuração

### Setup inicial
```bash
# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual (Linux/Mac)
source venv/bin/activate

# Ativar ambiente virtual (Windows)
venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt

# Copiar arquivo de ambiente
cp .env.example .env

# Criar migrações
python manage.py makemigrations

# Aplicar migrações
python manage.py migrate

# Criar superusuário
python manage.py createsuperuser

# Iniciar servidor
python manage.py runserver
```

---

##  Comandos de Banco de Dados

### Migrações
```bash
# Criar migrações para o app notifications
python manage.py makemigrations notifications

# Aplicar todas as migrações
python manage.py migrate

# Ver SQL das migrações
python manage.py sqlmigrate notifications 0001

# Reverter migrações
python manage.py migrate notifications zero

# Verificar status das migrações
python manage.py showmigrations
```

### Dados
```bash
# Abrir shell do Django
python manage.py shell

# Criar backup do banco
python manage.py dumpdata > backup.json

# Restaurar backup
python manage.py loaddata backup.json

# Limpar banco (cuidado!)
python manage.py flush
```

---

##  Testes

### Executar testes
```bash
# Todos os testes
python manage.py test

# Testes do app notifications
python manage.py test notifications

# Teste específico
python manage.py test notifications.tests.NotificationAPITest.test_send_notification_success

# Com verbosidade
python manage.py test --verbosity=2

# Manter banco de teste
python manage.py test --keepdb

# Executar em paralelo
python manage.py test --parallel
```

### Executar testes unitários e de integração
```bash
# Executar todos os testes
python manage.py test notifications

# Executar com verbosidade
python manage.py test notifications -v 2

# Executar teste específico
python manage.py test notifications.tests.NotificationAPITest

# Executar apenas testes de integração
python manage.py test notifications.tests.NotificationIntegrationTest
```

---

##  Inspeção e Debug

### Django Shell
```bash
# Abrir shell
python manage.py shell

# Exemplos de comandos no shell:
>>> from notifications.models import Notification
>>> Notification.objects.all()
>>> Notification.objects.filter(status='sent').count()
>>> from notifications.services import EmailService
>>> EmailService.send_notification('teste@example.com', 'Assunto', 'Mensagem')
```

### Verificar configurações
```bash
# Ver todas as configurações
python manage.py diffsettings

# Validar projeto
python manage.py check

# Verificar deploy (produção)
python manage.py check --deploy
```

---

##  Administração

### Gerenciar usuários
```bash
# Criar superusuário
python manage.py createsuperuser

# Alterar senha de usuário
python manage.py changepassword username
```

### Coletar arquivos estáticos (produção)
```bash
python manage.py collectstatic
```

---

##  API - Exemplos com cURL

### Enviar notificação
```bash
curl -X POST http://localhost:8000/api/notifications/send/ \
  -H "Content-Type: application/json" \
  -d '{
    "recipient_email": "usuario@example.com",
    "subject": "Bem-vindo!",
    "message": "Obrigado por se cadastrar!"
  }'
```

### Listar todas as notificações
```bash
curl http://localhost:8000/api/notifications/
```

### Listar com filtro
```bash
curl "http://localhost:8000/api/notifications/?status=sent"
```

### Obter detalhes de uma notificação
```bash
curl http://localhost:8000/api/notifications/1/
```

### Estatísticas
```bash
curl http://localhost:8000/api/notifications/statistics/
```

### Deletar notificação
```bash
curl -X DELETE http://localhost:8000/api/notifications/1/
```

### Com formatação (usando jq)
```bash
curl -s http://localhost:8000/api/notifications/statistics/ | jq
```

---

##  API - Exemplos com Python

### Usando requests
```python
import requests

# Enviar notificação
response = requests.post(
    'http://localhost:8000/api/notifications/send/',
    json={
        'recipient_email': 'usuario@example.com',
        'subject': 'Teste',
        'message': 'Mensagem de teste'
    }
)
print(response.json())

# Listar notificações
response = requests.get('http://localhost:8000/api/notifications/')
print(response.json())

# Estatísticas
response = requests.get('http://localhost:8000/api/notifications/statistics/')
print(response.json())
```

---

##  Testar Email

### Via Django Shell
```python
python manage.py shell

from django.core.mail import send_mail

send_mail(
    'Assunto do Email',
    'Corpo da mensagem',
    'remetente@example.com',
    ['destinatario@example.com'],
    fail_silently=False,
)
```

### Usando o serviço
```python
python manage.py shell

from notifications.services import EmailService

success, notification, error = EmailService.send_notification(
    recipient_email='teste@example.com',
    subject='Teste',
    message='Mensagem de teste'
)

print(f"Sucesso: {success}")
print(f"Notificação: {notification}")
print(f"Erro: {error}")
```

---

##  Manutenção

### Limpar cache
```bash
python manage.py clear_cache
```

### Ver logs
```bash
# Servidor em modo verbose
python manage.py runserver --verbosity 3

# Logs do Django (configure em settings.py)
tail -f logs/django.log
```

### Limpar notificações antigas
```python
python manage.py shell

from notifications.models import Notification
from datetime import timedelta
from django.utils import timezone

# Deletar notificações com mais de 30 dias
old_date = timezone.now() - timedelta(days=30)
Notification.objects.filter(created_at__lt=old_date).delete()
```

---

##  Segurança

### Gerar SECRET_KEY
```python
python manage.py shell

from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

### Verificar configurações de segurança
```bash
python manage.py check --deploy
```

---

##  Deploy

### Preparar para produção
```bash
# Coletar arquivos estáticos
python manage.py collectstatic --noinput

# Aplicar migrações
python manage.py migrate

# Verificar configurações
python manage.py check --deploy
```

### Usando Gunicorn (produção)
```bash
# Instalar
pip install gunicorn

# Executar
gunicorn config.wsgi:application --bind 0.0.0.0:8000
```

### Usando Docker
```bash
# Build
docker build -t notification-api .

# Run
docker run -p 8000:8000 notification-api
```

---

##  Git

### Comandos úteis
```bash
# Ver status
git status

# Adicionar arquivos
git add .

# Commit
git commit -m "Descrição da mudança"

# Push
git push origin main

# Ver histórico
git log --oneline

# Ver diferenças
git diff
```

---

##  Performance

### Analisar queries SQL
```python
python manage.py shell

from django.db import connection
from notifications.models import Notification

Notification.objects.filter(status='sent')
print(connection.queries)
```

### Contar objetos
```bash
python manage.py shell

from notifications.models import Notification

print(f"Total: {Notification.objects.count()}")
print(f"Enviados: {Notification.objects.filter(status='sent').count()}")
print(f"Falhos: {Notification.objects.filter(status='failed').count()}")
```

---

##  Troubleshooting

### Recriar banco de dados
```bash
# Apagar banco
rm db.sqlite3

# Recriar
python manage.py migrate

# Criar superusuário
python manage.py createsuperuser
```

### Reinstalar dependências
```bash
pip uninstall -r requirements.txt -y
pip install -r requirements.txt
```

### Verificar porta em uso
```bash
# Linux/Mac
lsof -i :8000

# Matar processo
kill -9 <PID>
```

---

##  Documentação

### Gerar documentação da API
```bash
# Usando drf-spectacular (opcional)
pip install drf-spectacular
python manage.py spectacular --file schema.yml
```

### Ver rotas disponíveis
```bash
python manage.py show_urls  # Requer django-extensions
```

---

##  Atalhos de Desenvolvimento

### Criar app novo
```bash
python manage.py startapp nome_do_app
```

### Formatar código (Black)
```bash
pip install black
black .
```

### Lint (Flake8)
```bash
pip install flake8
flake8 .
```

### Type checking (MyPy)
```bash
pip install mypy
mypy .
```

---

**Dica:** Salve este arquivo e consulte sempre que precisar! 
