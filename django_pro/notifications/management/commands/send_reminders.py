from django.core.management.base import BaseCommand

from ...constants import (
    BOOKINGS_FOUND_MSG,
    REMINDER_SENT_MSG,
    REMINDER_ERROR_MSG,
    REMINDER_COMPLETE_MSG,
)


class Command(BaseCommand):
    help = 'Отправляет напоминания о предстоящих записях'

    def handle(self, *args, **options):
        self.stdout.write('🔔 Запуск отправки напоминаний...')

        from ...reminder_utils import (
            get_bookings_needing_reminder,
            should_send_reminder,
            mark_reminder_sent,
        )
        from ...telegram_utils import send_reminder_notification

        bookings = get_bookings_needing_reminder()
        self.stdout.write(BOOKINGS_FOUND_MSG.format(len(bookings)))

        sent_count = 0
        for booking in bookings:
            if should_send_reminder(booking):
                try:
                    success = send_reminder_notification(booking)
                    if success:
                        mark_reminder_sent(booking)
                        sent_count += 1
                        self.stdout.write(
                            REMINDER_SENT_MSG.format(booking.client_name)
                        )
                except Exception as e:
                    self.stdout.write(
                        REMINDER_ERROR_MSG.format(booking.client_name, str(e))
                    )

        self.stdout.write(
            self.style.SUCCESS(REMINDER_COMPLETE_MSG.format(sent_count))
        )
