from django.core.management.base import BaseCommand
from booking.models import Booking
from notifications.telegram_utils import send_booking_notification


class Command(BaseCommand):
    """
    Проверим отправку тестового сообщения
    python manage.py diagnose_bot.
    """
    help = 'Тест отправки уведомления'

    def handle(self, *args, **options):
        self.stdout.write('🧪 Тест отправки уведомления...')

        # Берем последнее бронирование для теста
        booking = Booking.objects.last()
        if not booking:
            self.stdout.write('❌ Нет бронирований для теста')
            return

        self.stdout.write(f'📋 Тестовое бронирование: {booking.booking_id}')
        self.stdout.write(f'👤 Клиент: {booking.client_name}')
        self.stdout.write(f'👨‍💼 Мастер: {booking.master.name}')
        self.stdout.write(f'💬 Процедура: {booking.procedure.title}')

        success = send_booking_notification(booking)

        if success:
            self.stdout.write(
                self.style.SUCCESS(
                    '✅ Уведомление отправлено успешно!'
                    )
                )
        else:
            self.stdout.write(
                self.style.ERROR(
                    '❌ Не удалось отправить уведомление'
                    )
                )
