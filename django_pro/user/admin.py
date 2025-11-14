from django.contrib import admin

from .models import Client, PaymentSettings, User


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'phone',
        'email',
        'notification_method',
        'is_new',
        'always_prepayment',
        'created_at',
    ]
    list_filter = ['is_new', 'always_prepayment', 'created_at']
    search_fields = ['name', 'phone', 'email']
    list_editable = ['is_new', 'always_prepayment']
    readonly_fields = ['created_at']
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'phone', 'email')
        }),
        ('Статусы', {
            'fields': ('is_new', 'always_prepayment', 'notification_method')
        }),
        ('Системная информация', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(PaymentSettings)
class PaymentSettingsAdmin(admin.ModelAdmin):
    list_display = [
        'admin_phone',
        'master_phone',
        'prepayment_percent',
        'is_active',
    ]
    list_editable = ['is_active']


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'phone', 'email', 'first_name', 'last_name']
    list_filter = ['is_staff', 'is_active']
    search_fields = ['username', 'phone', 'email']
