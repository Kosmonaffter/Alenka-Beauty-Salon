from django.contrib import admin
from .models import Master


@admin.register(Master)
class MasterAdmin(admin.ModelAdmin):
    """Админка для мастеров."""

    list_display = [
        'name',
        'specialization',
        'phone',
        'is_contact_phone',
        'telegram_username',
        'is_active',
    ]
    list_filter = [
        'is_active',
        'is_contact_phone',
        'specialization',
    ]
    search_fields = [
        'name',
        'phone',
        'telegram_username',
    ]
    list_editable = ['is_active', 'is_contact_phone']
    filter_horizontal = ['procedures']

    # @admin.display(description='Телефон для справок', boolean=True)
    # def is_contact_phode_display(self, obj):
    #     return obj.is_contact_phone
