import uuid
from datetime import datetime, timedelta, time

from django.db import models

from user.models import Client
from .constants import (
    BOOKING_ID_MAX_LENGTH,
    DEFAULT_TIME_INTERVAL,
    DEFAULT_WORKING_END_HOUR,
    DEFAULT_WORKING_END_MINUTE,
    DEFAULT_WORKING_START_HOUR,
    DEFAULT_WORKING_START_MINUTE,
    NAME_MAX_LENGTH,
    NOTIFICATION_EMAIL,
    NOTIFICATION_METHOD_MAX_LENGTH,
    NOTIFICATION_TELEGRAM,
    PAYMENT_NOT_REQUIRED,
    PAYMENT_PAID,
    PAYMENT_PENDING,
    PAYMENT_STATUS_MAX_LENGTH,
    PHONE_MAX_LENGTH,
    STATUS_CANCELLED,
    STATUS_COMPLETED,
    STATUS_CONFIRMED,
    STATUS_MAX_LENGTH,
    STATUS_NO_SHOW,
    STATUS_PAID,
    STATUS_PENDING,
)


class Booking(models.Model):
    """Модель бронирования процедуры."""

    STATUS_CHOICES = [
        (STATUS_PENDING, '⏳ Ожидает подтверждения'),
        (STATUS_CONFIRMED, '✅ Подтверждено'),
        (STATUS_COMPLETED, '✅ Завершено'),
        (STATUS_CANCELLED, '❌ Отменено'),
        (STATUS_PAID, '💰 Оплачено'),
        (STATUS_NO_SHOW, '🚫 Не пришел'),
    ]

    NOTIFICATION_CHOICES = [
        (NOTIFICATION_TELEGRAM, 'Telegram'),
        (NOTIFICATION_EMAIL, 'Email'),
    ]

    PAYMENT_STATUS_CHOICES = [
        (PAYMENT_PENDING, '⏳ Ожидает оплаты'),
        (PAYMENT_PAID, '✅ Оплачено'),
        (PAYMENT_NOT_REQUIRED, '❌ Не требуется'),
    ]

    booking_id = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
        verbose_name='ID брони',
    )
    procedure = models.ForeignKey(
        'catalog.Procedure',
        on_delete=models.CASCADE,
        verbose_name='Процедура',
    )
    master = models.ForeignKey(
        'masters.Master',
        on_delete=models.CASCADE,
        verbose_name='Мастер',
    )
    booking_date = models.DateField(verbose_name='Дата записи')
    booking_time = models.TimeField(verbose_name='Время записи')
    client_phone = models.CharField(
        max_length=PHONE_MAX_LENGTH,
        verbose_name='Телефон клиента',
    )
    client_name = models.CharField(
        max_length=NAME_MAX_LENGTH,
        verbose_name='Имя клиента',
    )
    client_email = models.EmailField(
        blank=True,
        null=True,
        verbose_name='Email клиента',
    )
    notification_method = models.CharField(
        max_length=NOTIFICATION_METHOD_MAX_LENGTH,
        choices=NOTIFICATION_CHOICES,
        default=NOTIFICATION_TELEGRAM,
        verbose_name='Способ уведомления',
    )
    personal_data_agreement = models.BooleanField(
        default=False,
        verbose_name='Согласие на обработку данных',
    )
    status = models.CharField(
        max_length=STATUS_MAX_LENGTH,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
        verbose_name='Статус',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Создано',
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Обновлено',
    )
    confirmed_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Подтверждено',
    )
    telegram_message_id = models.CharField(
        max_length=BOOKING_ID_MAX_LENGTH,
        blank=True,
        null=True,
        verbose_name='ID сообщения в Telegram',
    )
    admin_notes = models.TextField(
        blank=True,
        verbose_name='Заметки администратора',
    )
    client = models.ForeignKey(
        Client,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Клиент',
    )
    payment_status = models.CharField(
        max_length=PAYMENT_STATUS_MAX_LENGTH,
        choices=PAYMENT_STATUS_CHOICES,
        default=PAYMENT_PENDING,
        verbose_name='Статус оплаты',
    )
    prepayment_required = models.BooleanField(
        default=False,
        verbose_name='Требуется предоплата',
    )
    payment_phone = models.CharField(
        max_length=PHONE_MAX_LENGTH,
        blank=True,
        verbose_name='Телефон для оплаты',
    )

    class Meta:
        verbose_name = 'Бронирование'
        verbose_name_plural = 'Бронирования'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['booking_date', 'booking_time', 'master']),
            models.Index(fields=['client_phone']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        procedure_title = (
            self.procedure.title if self.procedure else 'No Procedure'
        )
        return (
            f'{self.client_name} - {procedure_title} - '
            f'{self.booking_date} {self.booking_time}'
        )

    @property
    def booking_datetime(self):
        """Возвращает объединенную дату и время бронирования."""
        if self.booking_date and self.booking_time:
            return datetime.combine(self.booking_date, self.booking_time)
        return None

    @property
    def end_time(self):
        """Возвращает время окончания процедуры."""
        if (
            self.booking_datetime
            and self.procedure
            and self.procedure.duration
        ):
            duration_minutes = self.procedure.duration.total_seconds() / 60
            return self.booking_datetime + timedelta(minutes=duration_minutes)
        return self.booking_datetime


class WorkingHoursSettings(models.Model):
    """Настройки рабочего времени салона."""

    start_time = models.TimeField(
        default=time(DEFAULT_WORKING_START_HOUR, DEFAULT_WORKING_START_MINUTE),
        verbose_name='Начало рабочего дня',
    )
    end_time = models.TimeField(
        default=time(DEFAULT_WORKING_END_HOUR, DEFAULT_WORKING_END_MINUTE),
        verbose_name='Конец рабочего дня',
    )
    time_interval = models.PositiveIntegerField(
        default=DEFAULT_TIME_INTERVAL,
        verbose_name='Минимальный интервал между записями (минуты)',
        help_text='Минимальный интервал в минутах (рекомендуется 30)',
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Активные настройки',
    )

    class Meta:
        verbose_name = 'Настройка рабочего времени'
        verbose_name_plural = 'Настройки рабочего времени'

    def __str__(self):
        return f'Рабочее время: {self.start_time} - {self.end_time}'

    def save(self, *args, **kwargs):
        """Сохраняем только одну активную настройку."""
        if self.is_active:
            WorkingHoursSettings.objects.exclude(pk=self.pk).update(
                is_active=False
            )
        super().save(*args, **kwargs)
