from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.views.decorators.http import require_POST
import uuid
import json

from booking.models import Booking
from .constants import (
    CONTACT_SAVED_MESSAGE,
    INVALID_UUID_MESSAGE,
    START_MESSAGE,
    UNAUTHORIZED_MESSAGE,
    BOOKING_NOT_FOUND_MESSAGE,
)
from .models import ClientChat
from .reminder_utils import (
    process_reminder_confirmation,
    process_reminder_cancellation
)
from .telegram_utils import (
    answer_callback_query,
    create_contact_keyboard,
    send_telegram_message,
    send_client_notification
)


@csrf_exempt
@require_POST
def telegram_webhook(request):
    """Webhook для обработки команд из Telegram."""
    try:
        data = json.loads(request.body)

        # Обрабатываем контакт (номер телефона)
        if 'message' in data and 'contact' in data['message']:
            return handle_contact(data['message'])

        # Обрабатываем callback queries
        if 'callback_query' in data:
            return handle_callback_query(data['callback_query'])

        # Обрабатываем текстовые сообщения
        message = data.get('message', {})
        message_text = message.get('text', '')
        chat_id = message.get('chat', {}).get('id')

        # Команда /start
        if message_text == '/start':
            return handle_start_command(chat_id)

        # Команды подтверждения/отмены
        if message_text.startswith('/confirm_'):
            booking_id = message_text.replace('/confirm_', '').strip()
            if is_valid_uuid(booking_id):
                return confirm_booking(booking_id, chat_id)
            else:
                send_telegram_message(chat_id, INVALID_UUID_MESSAGE)
                return JsonResponse({'status': 'invalid_command'})

        if message_text.startswith('/cancel_'):
            booking_id = message_text.replace('/cancel_', '').strip()
            if is_valid_uuid(booking_id):
                return cancel_booking(booking_id, chat_id)
            else:
                send_telegram_message(chat_id, INVALID_UUID_MESSAGE)
                return JsonResponse({'status': 'invalid_command'})

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        print(f'Error: {e}')

    return JsonResponse({'status': 'ok'})


def is_valid_uuid(uuid_string):
    """Проверяет валидность UUID."""
    try:
        uuid.UUID(uuid_string)
        return True
    except ValueError:
        return False


def handle_contact(message):
    """Обрабатывает отправку контакта."""
    contact = message['contact']
    phone = contact.get('phone_number')
    chat_id = message['chat']['id']
    normalized_phone = phone if phone.startswith('+') else '+' + phone
    ClientChat.objects.update_or_create(
        phone=normalized_phone,
        defaults={'chat_id': chat_id}
    )

    send_telegram_message(chat_id, CONTACT_SAVED_MESSAGE)
    return JsonResponse({'status': 'contact_saved'})


def handle_start_command(chat_id):
    """Обрабатывает команду /start."""
    keyboard = create_contact_keyboard()
    send_telegram_message(chat_id, START_MESSAGE, reply_markup=keyboard)
    return JsonResponse({'status': 'start_handled'})


def handle_callback_query(data):
    """Обрабатывает нажатия на кнопки."""
    callback_data = data.get('data', '')
    chat_id = data.get('from', {}).get('id')

    if callback_data.startswith('reminder_confirm_'):
        booking_id = callback_data.replace('reminder_confirm_', '').strip()
        result = process_reminder_confirmation(booking_id)
        answer_callback_query(data['id'], "Запись подтверждена ✅")
        return JsonResponse({'status': 'reminder_confirmed'})

    elif callback_data.startswith('reminder_cancel_'):
        booking_id = callback_data.replace('reminder_cancel_', '').strip()
        result = process_reminder_cancellation(booking_id)
        answer_callback_query(data['id'], "Запись отменена ❌")
        return JsonResponse({'status': 'reminder_cancelled'})

    elif callback_data.startswith('confirm_'):
        booking_id = callback_data.replace('confirm_', '').strip()
        result = confirm_booking(booking_id, chat_id)
        answer_callback_query(data['id'], "Запись подтверждена ✅")
        return result

    elif callback_data.startswith('cancel_'):
        booking_id = callback_data.replace('cancel_', '').strip()
        result = cancel_booking(booking_id, chat_id)
        answer_callback_query(data['id'], "Запись отменена ❌")
        return result

    return JsonResponse({'status': 'unknown_command'})


def confirm_booking(booking_id, chat_id):
    """Подтверждение бронирования."""
    try:
        booking = Booking.objects.get(booking_id=booking_id)
        master_chat_id = str(
            booking.master.telegram_chat_id
        ) if booking.master.telegram_chat_id else None
        admin_chat_id = str(
            getattr(settings, 'TELEGRAM_ADMIN_CHAT_ID', '')
        )

        if str(chat_id) != master_chat_id and str(chat_id) != admin_chat_id:
            send_telegram_message(chat_id, UNAUTHORIZED_MESSAGE)
            return JsonResponse({'error': 'Unauthorized'}, status=403)

        # Обновляем статус
        booking.status = 'confirmed'
        booking.confirmed_at = timezone.now()
        booking.save()

        # Уведомляем клиента
        send_client_notification(booking, 'confirmed')

        # Уведомляем мастера
        send_telegram_message(
            chat_id,
            f'✅ Запись подтверждена!\nДата: {booking.booking_date} в '
            f'{booking.booking_time}\nТелефон: {booking.client_phone}'
            f'\nКлиент: {booking.client_name}'
        )

        return JsonResponse({'status': 'confirmed'})

    except Booking.DoesNotExist:
        send_telegram_message(chat_id, BOOKING_NOT_FOUND_MESSAGE)
        return JsonResponse({'error': 'Booking not found'}, status=404)


def cancel_booking(booking_id, chat_id):
    """Отмена бронирования."""
    try:
        booking = Booking.objects.get(booking_id=booking_id)
        master_chat_id = str(
            booking.master.telegram_chat_id
        ) if booking.master.telegram_chat_id else None
        admin_chat_id = str(getattr(settings, 'TELEGRAM_ADMIN_CHAT_ID', ''))

        if str(chat_id) != master_chat_id and str(chat_id) != admin_chat_id:
            send_telegram_message(chat_id, UNAUTHORIZED_MESSAGE)
            return JsonResponse({'error': 'Unauthorized'}, status=403)

        booking.status = 'cancelled'
        booking.save()

        send_client_notification(booking, 'cancelled')
        send_telegram_message(
            chat_id,
            f'❌ Запись {booking.booking_id} отменена.'
        )

        return JsonResponse({'status': 'cancelled'})

    except Booking.DoesNotExist:
        send_telegram_message(chat_id, BOOKING_NOT_FOUND_MESSAGE)
        return JsonResponse({'error': 'Booking not found'}, status=404)
