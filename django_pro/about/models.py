from django.db import models


class Address(models.Model):

    address = models.TextField(
        blank=True,
        verbose_name='Адрес',
    )
    map_embed_code = models.TextField(
        blank=True,
        verbose_name='Код для встраивания карты',
        help_text='HTML код для встраивания карты (iframe)',
    )
    is_legal_address = models.BooleanField(
        default=False,
        verbose_name='Юридический адрес',
        help_text=(
            'Использовать этот адрес для юридических документов и согласий'
        ),
    )
    is_display_address = models.BooleanField(
        default=False,
        verbose_name='Адрес для отображения',
        help_text='Использовать этот адрес на страницах сайта (about)',
    )

    class Meta:
        verbose_name = ('Адрес')
        verbose_name_plural = ("адреса")

    def __str__(self):
        return self.address

    def has_map(self):
        """Проверяет, есть ли код карты."""
        return bool(self.map_embed_code)

    def save(self, *args, **kwargs):
        """Автоматически снимаем галочки с других адресов при сохранении."""
        if self.is_legal_address:
            Address.objects.exclude(pk=self.pk).filter(
                is_legal_address=True
            ).update(is_legal_address=False)
        if self.is_display_address:
            Address.objects.exclude(pk=self.pk).filter(
                is_display_address=True
            ).update(is_display_address=False)
        super().save(*args, **kwargs)
