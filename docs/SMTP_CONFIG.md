# Guia de Configuração de Email SMTP

Este documento explica como configurar diferentes provedores de email para envio de notificações em produção.

##  Gmail

### Pré-requisitos
1. Ativar verificação em duas etapas na sua conta Google
2. Gerar uma senha de app em: https://myaccount.google.com/apppasswords

### Configuração no .env
```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=seu-email@gmail.com
EMAIL_HOST_PASSWORD=sua-senha-de-app
DEFAULT_FROM_EMAIL=seu-email@gmail.com
```

### Limitações
- Limite de 500 emails por dia para contas gratuitas
- Não recomendado para produção em larga escala

---

##  SendGrid

### Pré-requisitos
1. Criar conta em: https://sendgrid.com/
2. Gerar API Key no painel

### Instalação
```bash
pip install sendgrid
```

### Configuração no .env
```env
EMAIL_BACKEND=sendgrid_backend.SendgridBackend
SENDGRID_API_KEY=sua-api-key
DEFAULT_FROM_EMAIL=seu-email-verificado@seudominio.com
```

### Vantagens
- 100 emails/dia gratuitos
- Excelente deliverability
- Estatísticas detalhadas

---

##  AWS SES (Amazon Simple Email Service)

### Pré-requisitos
1. Conta AWS
2. Verificar domínio ou email no SES

### Instalação
```bash
pip install django-ses
```

### Configuração no .env
```env
EMAIL_BACKEND=django_ses.SESBackend
AWS_ACCESS_KEY_ID=sua-access-key
AWS_SECRET_ACCESS_KEY=sua-secret-key
AWS_SES_REGION_NAME=us-east-1
AWS_SES_REGION_ENDPOINT=email.us-east-1.amazonaws.com
DEFAULT_FROM_EMAIL=noreply@seudominio.com
```

### Vantagens
- Muito econômico (US$0.10 por 1000 emails)
- Alta escalabilidade
- Integração com outros serviços AWS

---

##  Mailgun

### Pré-requisitos
1. Criar conta em: https://www.mailgun.com/
2. Obter API Key e domínio

### Instalação
```bash
pip install django-mailgun
```

### Configuração no .env
```env
EMAIL_BACKEND=django_mailgun.MailgunBackend
MAILGUN_ACCESS_KEY=sua-api-key
MAILGUN_SERVER_NAME=mg.seudominio.com
DEFAULT_FROM_EMAIL=noreply@seudominio.com
```

### Vantagens
- 5.000 emails/mês gratuitos
- Fácil configuração
- API RESTful poderosa

---

##  Outlook/Office 365

### Configuração no .env
```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.office365.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=seu-email@outlook.com
EMAIL_HOST_PASSWORD=sua-senha
DEFAULT_FROM_EMAIL=seu-email@outlook.com
```

---

##  Configuração para Desenvolvimento

### Console Backend (Padrão)
Exibe emails no console/terminal - ideal para desenvolvimento:

```env
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

### File Backend
Salva emails em arquivos locais:

```env
EMAIL_BACKEND=django.core.mail.backends.filebased.EmailBackend
EMAIL_FILE_PATH=/tmp/app-emails
```

---

##  Testando a Configuração

### Via Django Shell
```python
python manage.py shell

from django.core.mail import send_mail

send_mail(
    'Teste de Email',
    'Mensagem de teste',
    'remetente@example.com',
    ['destinatario@example.com'],
    fail_silently=False,
)
```

### Via API
```bash
curl -X POST http://localhost:8000/api/notifications/send/ \
  -H "Content-Type: application/json" \
  -d '{
    "recipient_email": "destinatario@example.com",
    "subject": "Teste de Configuração",
    "message": "Se você recebeu este email, a configuração está correta!"
  }'
```

---

##  Boas Práticas de Segurança

1. **Nunca commite credenciais**: Use sempre `.env` e adicione ao `.gitignore`

2. **Use variáveis de ambiente**: Não hardcode senhas no código

3. **Rotacione credenciais**: Troque senhas/API keys regularmente

4. **Limite permissões**: Use credenciais com permissões mínimas necessárias

5. **Monitore uso**: Configure alertas para uso anormal

6. **Use HTTPS**: Sempre em produção

7. **Valide emails**: Implemente confirmação de email antes de enviar

---

##  Troubleshooting

### Email não está sendo enviado

1. Verifique as configurações no `.env`
2. Confira os logs do Django
3. Verifique o status no banco de dados (campo `status` e `error_message`)
4. Teste credenciais via telnet/openssl

### Erro de autenticação

1. Verifique usuário e senha
2. Para Gmail, use senha de app (não a senha normal)
3. Verifique se 2FA está ativo (Gmail)
4. Confirme que as portas não estão bloqueadas

### Emails indo para spam

1. Configure SPF, DKIM e DMARC no DNS
2. Use domínio verificado
3. Evite palavras de spam no assunto
4. Mantenha taxa de envio controlada
5. Use serviço profissional (SendGrid, AWS SES)

---

##  Comparação de Serviços

| Serviço | Gratuito | Custo | Fácil Setup | Recomendado Para |
|---------|----------|-------|-------------|------------------|
| Gmail | 500/dia | Grátis |  | Desenvolvimento |
| SendGrid | 100/dia | $$ |  | Produção pequena |
| AWS SES | - | $ |  | Produção grande |
| Mailgun | 5k/mês | $$ |  | Produção média |
| Outlook | - | Grátis* |  | Desenvolvimento |

*Requer conta Microsoft

---

##  Recursos Adicionais

- [Documentação Django - Email](https://docs.djangoproject.com/en/4.2/topics/email/)
- [SendGrid Documentation](https://docs.sendgrid.com/)
- [AWS SES Documentation](https://docs.aws.amazon.com/ses/)
- [Mailgun Documentation](https://documentation.mailgun.com/)
