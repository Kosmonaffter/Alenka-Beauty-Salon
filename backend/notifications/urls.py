from django.urls import path

from . import telegram_bot

app_name = 'notifications'

urlpatterns = [
    path(
        'telegram-webhook/',
        telegram_bot.telegram_webhook,
        name='telegram_webhook',
    ),
]
