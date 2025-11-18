from datetime import datetime
from django.utils import timezone

from booking.models import Booking, ReminderSettings
from .constants import SECONDS_IN_HOUR


def get_reminder_settings():
    """Возвращает активные настройки напоминаний."""
    settings = ReminderSettings.objects.filter(is_active=True).first()
    if not settings:
        settings = ReminderSettings.objects.create()
    return settings


def get_bookings_needing_reminder():
    """Возвращает бронирования, которым нужно отправить напоминание."""
    settings = get_reminder_settings()
    now = timezone.now()

    print(f'🔔 DEBUG: Поиск напоминаний за {settings.reminder_hours} часов')
    print(f'🕒 DEBUG: Сейчас: {now}')

    # Получаем ВСЕ подходящие бронирования
    bookings = Booking.objects.filter(
        status__in=['pending', 'confirmed'],
        reminder_sent=False,
        needs_confirmation=True
    ).select_related('procedure', 'master', 'client')

    print(f'📋 DEBUG: Всего подходящих бронирований: {bookings.count()}')

    # Фильтруем по времени
    result = []
    for booking in bookings:
        booking_datetime = datetime.combine(booking.booking_date, booking.booking_time)
        booking_datetime = timezone.make_aware(booking_datetime)

        time_until_booking = booking_datetime - now
        hours_until_booking = time_until_booking.total_seconds() / SECONDS_IN_HOUR

        print(
            f'  📅 DEBUG: {booking.client_name}: через {hours_until_booking:.1f} часов '
            f'({booking.booking_date} {booking.booking_time})'
        )

        # Если до записи осталось <= настроенного времени
        if 0 < hours_until_booking <= settings.reminder_hours:
            result.append(booking)
            print('    ✅ DEBUG: БУДЕТ НАПОМИНАНИЕ!')
        elif hours_until_booking <= 0:
            print('    ❌ DEBUG: Запись уже прошла')
        else:
            print('    ⏳ DEBUG: Еще рано, нужно подождать')

    return result


def should_send_reminder(booking):
    """Проверяет, нужно ли отправлять напоминание для бронирования."""
    if booking.reminder_sent or not booking.needs_confirmation:
        return False

    settings = get_reminder_settings()
    booking_datetime = datetime.combine(
        booking.booking_date,
        booking.booking_time
    )
    booking_datetime = timezone.make_aware(booking_datetime)

    time_until_booking = booking_datetime - timezone.now()
    hours_until_booking = time_until_booking.total_seconds() / SECONDS_IN_HOUR

    return hours_until_booking <= settings.reminder_hours


def mark_reminder_sent(booking):
    """Отмечает, что напоминание отправлено."""
    booking.reminder_sent = True
    booking.reminder_sent_at = timezone.now()
    booking.save()


def process_reminder_confirmation(booking_id):
    """Обрабатывает подтверждение записи клиентом."""
    try:
        booking = Booking.objects.get(booking_id=booking_id)
        booking.needs_confirmation = False
        booking.status = 'confirmed'
        booking.save()

        from .telegram_utils import send_confirmation_notification
        send_confirmation_notification(booking)
        return True
    except Booking.DoesNotExist:
        return False


def process_reminder_cancellation(booking_id):
    """Обрабатывает отмену записи клиентом."""
    try:
        booking = Booking.objects.get(booking_id=booking_id)
        booking.status = 'cancelled'
        booking.needs_confirmation = False
        booking.save()

        from .telegram_utils import send_cancellation_notification
        send_cancellation_notification(booking)
        return True
    except Booking.DoesNotExist:
        return False
