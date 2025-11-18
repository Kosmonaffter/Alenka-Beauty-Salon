from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Отправляет напоминания о предстоящих записях'

    def handle(self, *args, **options):
        self.stdout.write('🔔 Запуск отправки напоминаний...')
        # Импортируем здесь чтобы избежать circular imports
        from ...reminder_utils import (
            get_bookings_needing_reminder,
            should_send_reminder,
            mark_reminder_sent,
        )
        from ...telegram_utils import send_reminder_notification

        bookings = get_bookings_needing_reminder()
        self.stdout.write(f'📋 Найдено {len(bookings)} бронирований')

        sent_count = 0
        for booking in bookings:
            if should_send_reminder(booking):
                try:
                    success = send_reminder_notification(booking)
                    if success:
                        mark_reminder_sent(booking)
                        sent_count += 1
                        self.stdout.write(
                            f'✅ Напоминание для {booking.client_name}'
                        )
                except Exception as e:
                    self.stdout.write(
                        f'❌ Ошибка для {booking.client_name}: {str(e)}'
                    )

        self.stdout.write(
            self.style.SUCCESS(f'🎉 Отправлено {sent_count} напоминаний')
        )
