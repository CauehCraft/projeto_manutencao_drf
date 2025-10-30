# Sistema de Notificações - Django REST Framework

Sistema completo de notificações por email desenvolvido com Django REST Framework.

## Funcionalidades

- Envio de notificações por email
- **Prevenção automática de notificações duplicadas** - garante que cada notificação seja enviada apenas uma vez para cada usuário
- Histórico completo de notificações enviadas
- Estatísticas de envio (taxa de sucesso, falhas, etc.)
- Filtros por status de notificação
- API RESTful completa
- Validação de dados robusta
- Registro de erros detalhado

## Requisitos

- Python 3.8+
- pip
- virtualenv (recomendado)

## Instalação

### 1. Clone o repositório

```bash
git clone https://github.com/CauehCraft/projeto_manutencao_drf.git
cd projeto_manutencao_drf
```

### 2. Crie e ative um ambiente virtual

```bash
python -m venv venv

# Linux/Mac
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Configure as variáveis de ambiente

Copie o arquivo `.env.example` para `.env`:

```bash
cp .env.example .env
```

Edite o arquivo `.env` com suas configurações:

```env
# Django Settings
SECRET_KEY=sua-chave-secreta-aqui
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Email Settings - Para desenvolvimento (console)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

# Email Settings - Para produção (SMTP)
# EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
# EMAIL_HOST=smtp.gmail.com
# EMAIL_PORT=587
# EMAIL_USE_TLS=True
# EMAIL_HOST_USER=seu-email@gmail.com
# EMAIL_HOST_PASSWORD=sua-senha-de-app
# DEFAULT_FROM_EMAIL=noreply@example.com
```

### 5. Execute as migrações

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Crie um superusuário (opcional)

```bash
python manage.py createsuperuser
```

### 7. Inicie o servidor

```bash
python manage.py runserver
```

O servidor estará disponível em `http://localhost:8000`

## Endpoints da API

### 1. Enviar Notificação

POST `/api/notifications/send/`

Body:
```json
{
    "recipient_email": "destinatario@example.com",
    "subject": "Título da Notificação",
    "message": "Corpo da mensagem da notificação"
}
```

Resposta de Sucesso (201):
```json
{
    "success": true,
    "message": "Notificação enviada com sucesso!",
    "notification": {
        "id": 1,
        "recipient_email": "destinatario@example.com",
        "subject": "Título da Notificação",
        "message": "Corpo da mensagem da notificação",
        "status": "sent",
        "error_message": null,
        "created_at": "2025-10-16T10:30:00Z",
        "sent_at": "2025-10-16T10:30:01Z"
    }
}
```

### 2. Listar Notificações

GET `/api/notifications/`

Query Parameters (opcionais):
- `status`: Filtrar por status (`pending`, `sent`, `failed`)

Resposta:
```json
{
    "count": 10,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "recipient_email": "destinatario@example.com",
            "subject": "Título da Notificação",
            "message": "Corpo da mensagem",
            "status": "sent",
            "error_message": null,
            "created_at": "2025-10-16T10:30:00Z",
            "sent_at": "2025-10-16T10:30:01Z"
        }
    ]
}
```

### 3. Detalhes de uma Notificação

GET `/api/notifications/{id}/`

### 4. Estatísticas

GET `/api/notifications/statistics/`

Resposta:
```json
{
    "total": 100,
    "sent": 95,
    "failed": 3,
    "pending": 2,
    "success_rate": 95.0
}
```

### 5. Deletar Notificação

DELETE `/api/notifications/{id}/`

## Prevenção de Notificações Duplicadas

O sistema possui um mecanismo automático para evitar o envio de notificações duplicadas. Quando uma solicitação de envio é feita, o sistema verifica se já existe uma notificação idêntica que foi enviada com sucesso (status 'sent').

### Como funciona:

1. Antes de criar uma nova notificação, o sistema busca por notificações existentes com:
   - Mesmo `recipient_email` (destinatário)
   - Mesmo `subject` (assunto)
   - Mesma `message` (mensagem)
   - Status `sent` (enviada com sucesso)

2. Se uma notificação idêntica for encontrada:
   - O sistema **não cria** uma nova notificação
   - O sistema **não envia** um novo email
   - A notificação existente é retornada na resposta
   - Um log informativo é registrado

3. Se nenhuma notificação idêntica for encontrada:
   - Uma nova notificação é criada e enviada normalmente

### Exemplo:

```bash
# Primeira solicitação - cria notificação ID 1
curl -X POST http://localhost:8000/api/notifications/send/ \
  -H "Content-Type: application/json" \
  -d '{
    "recipient_email": "usuario@example.com",
    "subject": "Bem-vindo",
    "message": "Bem-vindo ao sistema!"
  }'
# Resposta: {"id": 1, "status": "sent", ...}

# Segunda solicitação idêntica - retorna notificação ID 1 (não envia novamente)
curl -X POST http://localhost:8000/api/notifications/send/ \
  -H "Content-Type: application/json" \
  -d '{
    "recipient_email": "usuario@example.com",
    "subject": "Bem-vindo",
    "message": "Bem-vindo ao sistema!"
  }'
# Resposta: {"id": 1, "status": "sent", ...} (mesma ID)
```

Isso garante que os usuários não recebam notificações repetitivas, evitando spam e melhorando a experiência do usuário.

## Testando a API

### Usando curl

```bash
# Enviar notificação
curl -X POST http://localhost:8000/api/notifications/send/ \
  -H "Content-Type: application/json" \
  -d '{
    "recipient_email": "teste@example.com",
    "subject": "Teste de Notificação",
    "message": "Esta é uma mensagem de teste"
  }'

# Listar notificações
curl http://localhost:8000/api/notifications/

# Estatísticas
curl http://localhost:8000/api/notifications/statistics/
```

### Usando Testes Automatizados

Execute os testes unitários e de integração:

```bash
python manage.py test notifications
```

Os testes incluem:
- Testes de modelo (Notification)
- Testes de serviço (EmailService)
- Testes de API (endpoints REST)
- Testes de integração (fluxos completos)

## Configuração de Email

### Desenvolvimento (Console Backend)

Por padrão, o projeto usa o `console` backend, que exibe os emails no terminal:

```python
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

### Produção (SMTP - Gmail, SendGrid, etc.)

Para configurar email em produção, consulte o guia completo em [`docs/SMTP_CONFIG.md`](docs/SMTP_CONFIG.md).

## Estrutura do Projeto

```
projeto_manutencao_drf/
├── config/                 # Configurações do Django
│   ├── settings.py        # Configurações principais
│   ├── urls.py            # URLs principais
│   └── ...
├── notifications/          # App de notificações
│   ├── models.py          # Modelo Notification
│   ├── serializers.py     # Serializers DRF
│   ├── views.py           # ViewSets
│   ├── services.py        # Lógica de negócio
│   ├── admin.py           # Admin do Django
│   ├── tests.py           # Testes (unitários e integração)
│   └── urls.py            # URLs do app
├── docs/                   # Documentação
│   ├── SMTP_CONFIG.md     # Guia de configuração SMTP
│   ├── RELATORIO_TESTES.md # Relatório de testes
│   ├── COMANDOS_UTEIS.md  # Comandos úteis
│   └── CONCLUSAO.md       # Resumo executivo
├── manage.py              # CLI do Django
├── requirements.txt       # Dependências
├── .env.example          # Exemplo de variáveis de ambiente
└── README.md             # Esta documentação
```

## Segurança

IMPORTANTE para Produção:

1. Altere o `SECRET_KEY` no `.env`
2. Configure `DEBUG=False`
3. Configure `ALLOWED_HOSTS` apropriadamente
4. Adicione autenticação aos endpoints (JWT, OAuth, etc.)
5. Use HTTPS
6. Configure CORS adequadamente
7. Use um banco de dados robusto (PostgreSQL, MySQL)

## Painel Administrativo

Acesse `/admin/` para gerenciar notificações via interface web:

1. Crie um superusuário: `python manage.py createsuperuser`
2. Acesse: `http://localhost:8000/admin/`
3. Login com suas credenciais

## Documentação Adicional

- [Guia de Configuração SMTP](docs/SMTP_CONFIG.md) - Como configurar email em produção (Gmail, SendGrid, AWS SES, etc.)
- [Comandos Úteis](docs/COMANDOS_UTEIS.md) - Lista de comandos úteis para desenvolvimento

## Troubleshooting

### Erro: "ModuleNotFoundError"
```bash
pip install -r requirements.txt
```

### Emails não estão sendo enviados
- Verifique as configurações de EMAIL no `.env`
- Confira os logs no console
- Verifique o status da notificação no admin ou via API
- Consulte o [Guia de Configuração SMTP](docs/SMTP_CONFIG.md)

### Erro de migração
```bash
python manage.py makemigrations
python manage.py migrate
```

Para mais comandos úteis, consulte [`docs/COMANDOS_UTEIS.md`](docs/COMANDOS_UTEIS.md).