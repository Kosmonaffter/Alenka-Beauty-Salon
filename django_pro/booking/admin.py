from django.contrib import admin

from .models import Booking, WorkingHoursSettings, ReminderSettings


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    """Админка для бронирований."""

    list_display = [
        'booking_id',
        'client_name',
        'procedure',
        'master',
        'booking_date',
        'booking_time',
        'status'
    ]
    list_filter = [
        'status',
        'booking_date',
        'master',
        'procedure'
    ]
    search_fields = [
        'client_name',
        'client_phone',
        'booking_id'
    ]
    readonly_fields = [
        'booking_id',
        'created_at',
        'updated_at'
    ]
    list_editable = ['status']
    date_hierarchy = 'booking_date'
    fieldsets = (
        ('Основная информация', {
            'fields': (
                'booking_id',
                'procedure',
                'master',
                'booking_date',
                'booking_time'
            )
        }),
        ('Информация о клиенте', {
            'fields': (
                'client_name',
                'client_phone',
                'client_email',
                'personal_data_agreement'
            )
        }),
        ('Статус', {
            'fields': (
                'status',
                'confirmed_at',
                'admin_notes'
            )
        }),
        ('Системная информация', {
            'fields': (
                'created_at',
                'updated_at',
                'telegram_message_id'
            ),
            'classes': ('collapse',)
        }),
    )


@admin.register(WorkingHoursSettings)
class WorkingHoursSettingsAdmin(admin.ModelAdmin):
    """Админка для настроек рабочего времени."""

    list_display = ['start_time', 'end_time', 'time_interval', 'is_active']
    list_editable = ['is_active']

    def has_add_permission(self, request):
        """Ограничиваем создание только одной настройки."""
        if WorkingHoursSettings.objects.exists():
            return False
        return super().has_add_permission(request)


@admin.register(ReminderSettings)
class ReminderSettingsAdmin(admin.ModelAdmin):
    """Админка для настроек напоминаний."""
    list_display = ['reminder_hours', 'is_active']
    list_editable = ['is_active']

    def has_add_permission(self, request):
        """Ограничиваем создание только одной настройки."""
        if ReminderSettings.objects.exists():
            return False
        return super().has_add_permission(request)
