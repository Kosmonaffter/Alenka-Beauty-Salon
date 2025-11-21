from decimal import Decimal
from django.db import models
from django.utils import timezone


class Category(models.Model):
    """Категория процедур"""
    title = models.CharField(
        max_length=128,
        verbose_name='Название категории'
    )
    short_description = models.CharField(
        max_length=30,
        verbose_name='Короткое описание',
        help_text='До 30 символов для списка категорий',
        blank=True
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Активная категория'
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['title']


class Procedure(models.Model):
    """Конкретная процедура"""
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        verbose_name='Категория',
        related_name='procedures'
    )
    title = models.CharField(
        max_length=128,
        verbose_name='Название процедуры'
    )
    short_description = models.CharField(
        max_length=30,
        verbose_name='Короткое описание',
        help_text='До 30 символов (будет показано в списке)'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Полное описание'
    )
    image = models.ImageField(
        upload_to='procedures/',
        verbose_name='Фото процедуры',
        blank=True,
        null=True
    )
    duration = models.DurationField(
        default=timezone.timedelta(minutes=60),
        verbose_name='Продолжительность'
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Цена',
        default=Decimal('0.00')
    )
    is_available = models.BooleanField(
        default=True,
        verbose_name='Доступна для записи'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )

    def __str__(self):
        return f'{self.title} ({self.category})'

    class Meta:
        verbose_name = 'Процедура'
        verbose_name_plural = 'Процедуры'
        ordering = ['title']
