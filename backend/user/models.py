from django.db import models
from django.contrib.auth.models import AbstractUser

from .constants import (
    CLIENT_NAME_MAX_LENGTH,
    CLIENT_NOTIFICATION_CHOICES,
    CLIENT_NOTIFICATION_METHOD_MAX_LENGTH,
    CLIENT_NOTIFICATION_EMAIL,
    CLIENT_PHONE_MAX_LENGTH,
    PAYMENT_PHONE_MAX_LENGTH,
    PAYMENT_PREPAYMENT_PERCENT_DEFAULT,
    USER_PHONE_MAX_LENGTH,
)
from .permissions import UserPermissions


class Client(models.Model):
    """Модель клиента."""

    phone = models.CharField(
        max_length=CLIENT_PHONE_MAX_LENGTH,
        unique=True,
        verbose_name='Телефон'
    )
    name = models.CharField(
        max_length=CLIENT_NAME_MAX_LENGTH,
        verbose_name='Имя'
    )
    email = models.EmailField(
        blank=True,
        null=True,
        verbose_name='Email',
    )
    notification_method = models.CharField(
        max_length=CLIENT_NOTIFICATION_METHOD_MAX_LENGTH,
        choices=CLIENT_NOTIFICATION_CHOICES,
        default=CLIENT_NOTIFICATION_EMAIL,
        verbose_name='Способ уведомления'
    )
    is_new = models.BooleanField(
        default=True,
        verbose_name='Новый клиент'
    )
    always_prepayment = models.BooleanField(
        default=False,
        verbose_name='Всегда требовать предоплату',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата регистрации'
    )

    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'

    def __str__(self):
        return f'{self.name} ({self.phone})'


class PaymentSettings(models.Model):
    """Настройки оплаты."""

    admin_phone = models.CharField(
        max_length=PAYMENT_PHONE_MAX_LENGTH,
        verbose_name='Телефон администратора для оплаты'
    )
    master_phone = models.CharField(
        max_length=PAYMENT_PHONE_MAX_LENGTH,
        verbose_name='Телефон мастера для оплаты',
        blank=True
    )
    prepayment_percent = models.PositiveIntegerField(
        default=PAYMENT_PREPAYMENT_PERCENT_DEFAULT,
        verbose_name='Процент предоплаты для новых клиентов'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Активные настройки'
    )

    class Meta:
        verbose_name = 'Настройка оплаты'
        verbose_name_plural = 'Настройки оплаты'

    def __str__(self):
        return 'Настройки оплаты'

    def save(self, *args, **kwargs):
        """Сохраняем только одну активную настройку."""
        if self.is_active:
            PaymentSettings.objects.exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)


class User(AbstractUser):
    """Кастомная модель пользователя."""

    phone = models.CharField(
        max_length=USER_PHONE_MAX_LENGTH,
        blank=True,
        verbose_name='Телефон'
    )
    birth_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='Дата рождения',
    )
    groups = UserPermissions.get_groups_field()
    user_permissions = UserPermissions.get_user_permissions_field()

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
