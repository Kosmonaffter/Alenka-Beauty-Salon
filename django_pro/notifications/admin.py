from django.contrib import admin
from .models import TelegramBot, ClientChat


@admin.register(TelegramBot)
class TelegramBotAdmin(admin.ModelAdmin):
    list_display = ['name', 'token', 'is_active']
    list_editable = ['is_active']


@admin.register(ClientChat)
class ClientChatAdmin(admin.ModelAdmin):
    list_display = ['phone', 'chat_id', 'created_at']
    search_fields = ['phone', 'chat_id']
    readonly_fields = ['created_at']
