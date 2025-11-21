from django.db import models


class Master(models.Model):
    """Модель мастера/специалиста."""

    name = models.CharField(
        max_length=100,
        verbose_name='Имя мастера'
    )
    specialization = models.TextField(verbose_name='Специализация')
    photo = models.ImageField(
        upload_to='masters/',
        verbose_name='Фото',
        blank=True,
        null=True
    )
    telegram_username = models.CharField(
        max_length=100,
        verbose_name='Telegram username',
        blank=True,
        null=True
    )
    telegram_chat_id = models.CharField(
        max_length=50,
        verbose_name='Telegram Chat ID',
        blank=True,
        null=True
    )
    phone = models.CharField(
        max_length=20,
        verbose_name='Телефон мастера'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Активен'
    )
    description = models.TextField(
        verbose_name='Описание мастера',
        blank=True
    )
    procedures = models.ManyToManyField(
        'catalog.Procedure',
        verbose_name='Доступные процедуры',
        blank=True
    )
    age = models.IntegerField(verbose_name='Возраст', blank=True)
    is_contact_phone = models.BooleanField(
        default=False,
        verbose_name='Телефон для справок',
        help_text=(
            'Использовать этот телефон для уведомлений клиентов '
            '(работает даже если мастер не активен)'
        ),
    )

    class Meta:
        verbose_name = 'Мастер'
        verbose_name_plural = 'Мастера'
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.specialization})'
