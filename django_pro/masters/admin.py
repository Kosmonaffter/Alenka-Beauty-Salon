from django.contrib import admin
from .models import Master


@admin.register(Master)
class MasterAdmin(admin.ModelAdmin):
    """Админка для мастеров."""

    list_display = [
        'name',
        'specialization',
        'phone',
        'telegram_username',
        'is_active'
    ]
    list_filter = [
        'is_active',
        'specialization'
    ]
    search_fields = [
        'name',
        'phone',
        'telegram_username'
    ]
    list_editable = ['is_active']
    filter_horizontal = ['procedures']
