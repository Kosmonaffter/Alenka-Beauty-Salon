from django.db import models
from .constants import (
    NAME_MAX_LENGTH,
    TOKEN_MAX_LENGTH,
    PHONE_MAX_LENGTH,
    CHAT_ID_MAX_LENGTH,
)


class TelegramBot(models.Model):
    name = models.CharField(
        max_length=NAME_MAX_LENGTH,
        verbose_name='Название бота',
        default='Основной бот'
    )
    token = models.CharField(
        max_length=TOKEN_MAX_LENGTH,
        verbose_name='Токен бота',
        blank=True
    )
    admin_chat_id = models.CharField(
        max_length=CHAT_ID_MAX_LENGTH,
        verbose_name='Chat ID администратора',
        blank=True,
        help_text='ID чата для уведомлений администратора',
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Активный бот',
    )

    class Meta:
        verbose_name = 'Telegram бот'
        verbose_name_plural = 'Telegram боты'

    def __str__(self):
        return self.name


class ClientChat(models.Model):
    phone = models.CharField(
        max_length=PHONE_MAX_LENGTH,
        unique=True,
        verbose_name='Номер',
    )
    chat_id = models.CharField(
        max_length=CHAT_ID_MAX_LENGTH,
        verbose_name='Chat ID',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Создано',
    )

    class Meta:
        verbose_name = 'Chat клиента'
        verbose_name_plural = 'Chats клиентов'

    def __str__(self):
        return f'{self.phone} -> {self.chat_id}'
