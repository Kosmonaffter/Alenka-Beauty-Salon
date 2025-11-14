from django.db import models


class Address(models.Model):

    address = models.TextField(
        blank=True,
        verbose_name='Адрес',
    )
    map_embed_code = models.TextField(
        blank=True,
        verbose_name='Код для встраивания карты',
        help_text='HTML код для встраивания карты (iframe)'
    )

    class Meta:
        verbose_name = ('Адрес')
        verbose_name_plural = ("адреса")

    def __str__(self):
        return self.address

    def has_map(self):
        """Проверяет, есть ли код карты."""
        return bool(self.map_embed_code)
