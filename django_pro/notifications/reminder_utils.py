# notifications/reminder_utils.py
from datetime import datetime, timedelta
from django.utils import timezone

from booking.models import Booking, ReminderSettings
from .telegram_utils import send_confirmation_notification
from .constants import (
    REMINDER_ELIGIBLE_STATUSES,
    REMINDER_SEARCH_MSG,
    MOSCOW_TIME_MSG,
    BOOKINGS_COUNT_MSG,
    BOOKING_INFO_MSG,
    BOOKING_DATETIME_MSG,
    REMINDER_TIME_MSG,
    TIME_UNTIL_MSG,
    WILL_SEND_REMINDER_MSG,
    WONT_SEND_REMINDER_MSG,
    REMINDER_ALREADY_SENT_MSG,
    NO_CONFIRMATION_NEEDED_MSG,
    SENDING_REMINDER_MSG,
    NOT_SENDING_REMINDER_MSG,
    REMINDER_MARKED_SENT_MSG,
    SECONDS_IN_HOUR,
    ZERO_SECONDS,
)


def get_reminder_settings():
    """Возвращает активные настройки напоминаний."""
    settings = ReminderSettings.objects.filter(is_active=True).first()
    if not settings:
        settings = ReminderSettings.objects.create()
    return settings


def calculate_reminder_time(booking_datetime, reminder_hours):
    """Вычисляет время отправки напоминания."""
    return booking_datetime - timedelta(hours=reminder_hours)


def get_time_until_reminder(reminder_time, current_time):
    """Вычисляет время до напоминания."""
    return reminder_time - current_time


def get_bookings_needing_reminder():
    """Возвращает бронирования, которым нужно отправить напоминание."""
    settings = get_reminder_settings()
    now_local = timezone.localtime(timezone.now())

    print(REMINDER_SEARCH_MSG.format(settings.reminder_hours))
    print(MOSCOW_TIME_MSG.format(now_local))

    bookings = Booking.objects.filter(
        status__in=REMINDER_ELIGIBLE_STATUSES,
        reminder_sent=False,
        needs_confirmation=True,
    ).select_related('procedure', 'master', 'client')

    print(BOOKINGS_COUNT_MSG.format(bookings.count()))

    result = []
    for booking in bookings:
        booking_datetime_naive = datetime.combine(
            booking.booking_date,
            booking.booking_time,
        )
        booking_datetime_local = timezone.make_aware(
            booking_datetime_naive,
            timezone.get_current_timezone(),
        )

        reminder_time_local = calculate_reminder_time(
            booking_datetime_local,
            settings.reminder_hours
        )

        time_until_reminder = get_time_until_reminder(
            reminder_time_local,
            now_local
        )

        print(BOOKING_INFO_MSG.format(booking.client_name))
        print(BOOKING_DATETIME_MSG.format(booking_datetime_local))
        print(REMINDER_TIME_MSG.format(reminder_time_local))
        print(TIME_UNTIL_MSG.format(time_until_reminder))

        if time_until_reminder.total_seconds() <= ZERO_SECONDS:
            result.append(booking)
            print(WILL_SEND_REMINDER_MSG)
        else:
            print(WONT_SEND_REMINDER_MSG)

    return result


def should_send_reminder(booking):
    """Проверяет, нужно ли отправлять напоминание для бронирования."""
    if booking.reminder_sent:
        print(REMINDER_ALREADY_SENT_MSG.format(booking.client_name))
        return False

    if not booking.needs_confirmation:
        print(NO_CONFIRMATION_NEEDED_MSG.format(booking.client_name))
        return False

    settings = get_reminder_settings()
    now_local = timezone.localtime(timezone.now())

    booking_datetime_naive = datetime.combine(
        booking.booking_date,
        booking.booking_time,
    )
    booking_datetime_local = timezone.make_aware(
        booking_datetime_naive,
        timezone.get_current_timezone(),
    )

    reminder_time_local = calculate_reminder_time(
        booking_datetime_local,
        settings.reminder_hours
    )

    time_until_reminder = get_time_until_reminder(
        reminder_time_local,
        now_local
    )

    print(f'⏰ {booking.client_name}:')
    print(f'   Сейчас: {now_local}')
    print(f'   Запись: {booking_datetime_local}')
    print(f'   Напоминание: {reminder_time_local}')
    print(f'   До напоминания: {time_until_reminder}')

    should_send = time_until_reminder.total_seconds() <= ZERO_SECONDS

    if should_send:
        print(SENDING_REMINDER_MSG.format(booking.client_name))
    else:
        print(NOT_SENDING_REMINDER_MSG.format(booking.client_name))

    return should_send


def mark_reminder_sent(booking):
    """Отмечает, что напоминание отправлено."""
    booking.reminder_sent = True
    booking.reminder_sent_at = timezone.now()
    booking.save()
    print(REMINDER_MARKED_SENT_MSG.format(booking.client_name))


def process_reminder_confirmation(booking_id):
    """Обрабатывает подтверждение записи клиентом."""
    try:
        booking = Booking.objects.get(booking_id=booking_id)
        booking.needs_confirmation = False
        booking.status = 'confirmed'
        booking.save()

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
        send_confirmation_notification(booking)
        return True
    except Booking.DoesNotExist:
        return False


def schedule_reminder_for_booking(booking, save_changes=True):
    """
    Запланировать напоминание для бронирования.
    Вызывается при подтверждении записи.

    Args:
        booking: Объект бронирования
        save_changes: Сохранять ли изменения в базе (по умолчанию True)
    """
    try:
        settings = get_reminder_settings()
        booking_datetime_naive = datetime.combine(
            booking.booking_date,
            booking.booking_time,
        )
        booking_datetime_local = timezone.make_aware(
            booking_datetime_naive,
            timezone.get_current_timezone(),
        )
        reminder_time = calculate_reminder_time(
            booking_datetime_local,
            settings.reminder_hours
        )
        now_local = timezone.localtime(timezone.now())
        time_until_reminder = get_time_until_reminder(reminder_time, now_local)

        print('🎯 Запланировано напоминание:')
        print(f'   Клиент: {booking.client_name}')
        print(f'   Запись: {booking_datetime_local}')
        print(f'   Напоминание в: {reminder_time}')
        print(
            f'   Осталось часов: '
            f'{time_until_reminder.total_seconds() / SECONDS_IN_HOUR:.1f}'
        )
        booking.reminder_sent = False
        booking.reminder_sent_at = None
        booking.needs_confirmation = True

        if save_changes:
            booking.save()

        return True

    except Exception as e:
        print(f'❌ Ошибка планирования напоминания: {e}')
        return False
