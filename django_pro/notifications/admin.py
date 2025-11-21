from django.contrib import admin
from .models import TelegramBot, ClientChat


@admin.register(TelegramBot)
class TelegramBotAdmin(admin.ModelAdmin):
    list_display = ['name', 'token_preview', 'admin_chat_preview', 'is_active']
    list_editable = ['is_active']
    readonly_fields = ['token_preview', 'admin_chat_preview']
    fields = ['name', 'token', 'admin_chat_id', 'is_active']

    def token_preview(self, obj):
        if obj.token:
            return f'{obj.token[:10]}...' if len(obj.token) > 10 else obj.token
        return 'Не установлен'
    token_preview.short_description = 'Токен'  # type: ignore

    def admin_chat_preview(self, obj):
        return obj.admin_chat_id if obj.admin_chat_id else 'Не установлен'
    admin_chat_preview.short_description = (  # type: ignore
        'Chat ID администратора'
    )


@admin.register(ClientChat)
class ClientChatAdmin(admin.ModelAdmin):
    list_display = ['phone', 'chat_id', 'created_at']
    search_fields = ['phone', 'chat_id']
    readonly_fields = ['created_at']
