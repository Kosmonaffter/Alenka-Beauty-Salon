from django.db import models


class UserPermissions:
    """Permissions для кастомной модели User."""

    @classmethod
    def get_groups_field(cls):
        """Поле groups с уникальным related_name."""
        return models.ManyToManyField(
            'auth.Group',
            verbose_name='groups',
            blank=True,
            help_text='The groups this user belongs to.',
            related_name='custom_user_groups',
            related_query_name='custom_user',
        )

    @classmethod
    def get_user_permissions_field(cls):
        """Поле user_permissions с уникальным related_name."""
        return models.ManyToManyField(
            'auth.Permission',
            verbose_name='user permissions',
            blank=True,
            help_text='Specific permissions for this user.',
            related_name='custom_user_permissions',
            related_query_name='custom_user',
        )
