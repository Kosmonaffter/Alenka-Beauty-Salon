from django.db import models
from decimal import Decimal


class HomePageContent(models.Model):
    """Модель для контента главной страницы"""
    title = models.CharField(
        max_length=200,
        verbose_name='Заголовок страницы',
        default='Добро пожаловать в наш салон!'
    )
    main_description = models.TextField(
        verbose_name='Основное описание',
        help_text='Основной текст под заголовком'
    )
    service_title = models.CharField(
        max_length=200,
        verbose_name='Заголовок услуги',
        default='Массаж R-sleek – коррекция фигуры'
    )
    service_description = models.TextField(
        verbose_name='Описание услуги',
        help_text='Подробное описание основной услуги'
    )
    how_it_works = models.TextField(
        verbose_name='Как работает процедура?',
        help_text='Описание механизма работы процедуры'
    )
    mechanisms = models.TextField(
        verbose_name='Механизмы действия',
        help_text='Основные механизмы действия (каждый пункт с новой строки)'
    )
    features = models.TextField(
        verbose_name='Особенности массажа',
        help_text='Особенности аппаратного массажа'
    )
    problems = models.TextField(
        verbose_name='Решаемые проблемы',
        help_text=(
            'Проблемы, с которыми справляется массаж '
            '(каждый пункт с новой строки)'
        )
    )
    stages = models.TextField(
        verbose_name='Этапы процедуры',
        help_text='Описание этапов процедуры'
    )
    advantages = models.TextField(
        verbose_name='Преимущества',
        help_text='Преимущества массажа (каждый пункт с новой строки)'
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Цена за сеанс',
        default=Decimal('8000.00')
    )
    price_description = models.TextField(
        verbose_name='Описание цены',
        default=(
            'Высококлассные специалисты, безопасность и привлекательные цены'
        )
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Активно'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )

    def __str__(self):
        return 'Контент главной страницы'

    class Meta:
        verbose_name = 'Контент главной страницы'
        verbose_name_plural = 'Контент главной страницы'


class ContentImage(models.Model):
    """Модель для картинок контента"""
    content = models.ForeignKey(
        HomePageContent,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name='Контент'
    )
    image = models.ImageField(
        upload_to='content_images/',
        verbose_name='Изображение'
    )
    caption = models.CharField(
        max_length=200,
        verbose_name='Подпись',
        blank=True
    )
    position = models.CharField(
        max_length=20,
        choices=[
            ('mechanisms', 'Для механизмов действия'),
            ('problems', 'Для решаемых проблем'),
            ('advantages', 'Для преимуществ'),
            ('stages', 'Для этапов процедуры'),
            ('general', 'Общее изображение')
        ],
        default='general',
        verbose_name='Позиция'
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name='Порядок'
    )

    class Meta:
        ordering = ['position', 'order']
        verbose_name = 'Изображение контента'
        verbose_name_plural = 'Изображения контента'

    def __str__(self):
        return f'Изображение для {self.content}'
