from django.contrib import admin
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['subject', 'recipient_email', 'status', 'created_at', 'sent_at']
    list_filter = ['status', 'created_at', 'sent_at']
    search_fields = ['recipient_email', 'subject', 'message']
    readonly_fields = ['created_at', 'sent_at']
    
    fieldsets = (
        ('Informações do Email', {
            'fields': ('recipient_email', 'subject', 'message')
        }),
        ('Status', {
            'fields': ('status', 'error_message')
        }),
        ('Datas', {
            'fields': ('created_at', 'sent_at')
        }),
    )
