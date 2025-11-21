import requests
from django.conf import settings
from django.core.mail import send_mail
from http import HTTPStatus

from about.utils import get_contact_phone
from about.views import get_salon_address
from masters.models import Master
from .constants import (
    BOOKING_CREATED_TEMPLATE,
    CANCEL_BUTTON_TEXT,
    CANCELLATION_TELEGRAM_TEMPLATE,
    CLIENT_CONFIRMED_TEMPLATE,
    CLIENT_CANCELLED_TEMPLATE,
    CONFIRM_BUTTON_TEXT,
    CONFIRMED_EMAIL_TEMPLATE,
    CONFIRMATION_TELEGRAM_TEMPLATE,
    REMINDER_EMAIL_TEMPLATE,
    REMINDER_TELEGRAM_TEMPLATE,
    SECONDS_IN_MINUTE,
)
from .models import ClientChat, TelegramBot
from .personal_sender import send_personal_telegram_message


def send_email_notification(booking, notification_type):
    """Отправляет уведомление по email."""
    if not booking.client_email:
        print(f'DEBUG: Нет email клиента - {booking.client_email}')
        return False

    templates = {'confirmed': CONFIRMED_EMAIL_TEMPLATE}

    if notification_type not in templates:
        print(f'DEBUG: Неизвестный тип уведомления - {notification_type}')
        return False

    try:
        formatted_message = templates[notification_type].format(
            client_name=booking.client_name,
            procedure_title=booking.procedure.title,
            master_name=booking.master.name,
            master_phone=get_contact_phone(),
            booking_date=booking.booking_date,
            booking_time=booking.booking_time.strftime('%H:%M'),
            address=get_salon_address(),
        )
        send_mail(
            subject='✅ Подтверждение записи в салоне красоты',
            message=formatted_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[booking.client_email],
            fail_silently=False,
        )
        print('DEBUG: Email отправлен успешно!')
        return True
    except Exception as e:
        print(f'DEBUG: Ошибка отправки email: {str(e)}')
        import traceback

        print(f'DEBUG: Полная трассировка: {traceback.format_exc()}')
        return False


def send_telegram_message(chat_id, message, reply_markup=None):
    """Отправляет сообщение в Telegram."""
    bot = TelegramBot.objects.filter(is_active=True).first()
    if not bot:
        return False

    url = f'https://api.telegram.org/bot{bot.token}/sendMessage'
    payload = {'chat_id': chat_id, 'text': message, 'parse_mode': 'HTML'}

    if reply_markup:
        payload['reply_markup'] = reply_markup

    try:
        response = requests.post(url, json=payload, timeout=10)
        return response.status_code == HTTPStatus.OK
    except Exception:
        return False


def create_inline_keyboard(booking_id):
    """Создает клавиатуру для подтверждения/отмены."""
    return {
        'inline_keyboard': [
            [
                {
                    'text': '✅ Подтвердить',
                    'callback_data': f'confirm_{booking_id}',
                },
                {
                    'text': '❌ Отменить',
                    'callback_data': f'cancel_{booking_id}',
                },
            ]
        ]
    }


def create_contact_keyboard():
    """Создает клавиатуру для отправки номера."""
    return {
        'keyboard': [
            [
                {
                    'text': '📱 Отправить номер',
                    'request_contact': True,
                }
            ]
        ],
        'resize_keyboard': True,
        'one_time_keyboard': True,
    }


def find_chat_id_by_phone(phone):
    """Находит chat_id по номеру телефона."""
    try:
        client_chat = ClientChat.objects.filter(phone=phone).first()
        print(f'DEBAG chat_id по номеру телефона = {client_chat}')
        return client_chat.chat_id if client_chat else None
    except Exception:
        return None


def get_admin_chat_id():
    """Получает chat_id администратора."""
    bot = TelegramBot.objects.filter(is_active=True).first()
    if bot and bot.admin_chat_id:
        return bot.admin_chat_id
    # Потом из мастера с is_contact_phone=True
    admin_master = Master.objects.filter(
        is_contact_phone=True
    ).first()
    if admin_master and admin_master.telegram_chat_id:
        return admin_master.telegram_chat_id
    # Или из settings
    return getattr(settings, 'TELEGRAM_ADMIN_CHAT_ID', '')


def send_booking_notification(booking):
    """Отправляет уведомление о новом бронировании."""
    print(
        f'🔔 DEBUG: Начало отправки уведомления для брони {booking.booking_id}'
    )
    try:
        bot = TelegramBot.objects.filter(is_active=True).first()
        if not bot or not bot.token:
            print('❌ DEBUG: Бот не настроен')
            return False
        chat_id = get_admin_chat_id()
        print(f'🔔 DEBUG: Итоговый Chat ID для отправки: {chat_id}')
        if not chat_id:
            print('❌ DEBUG: Не указан chat_id для отправки')
            return False

        # Формируем сообщение
        duration = int(
            booking.procedure.duration.total_seconds() / SECONDS_IN_MINUTE
        )

        new_client_text = ''
        payment_info = ''

        if booking.prepayment_required:
            new_client_text = '🆕 <b>НОВЫЙ КЛИЕНТ - ТРЕБУЕТСЯ ПРЕДОПЛАТА</b>'
            payment_info = (
                f'💳 <b>Требуется предоплата:</b> '
                f'{booking.procedure.price} руб.\n'
            )

        message = BOOKING_CREATED_TEMPLATE.format(
            new_client_text=new_client_text,
            client_name=booking.client_name,
            client_phone=booking.client_phone,
            procedure_title=booking.procedure.title,
            procedure_price=booking.procedure.price,
            duration_minutes=duration,
            master_name=booking.master.name,
            booking_date=booking.booking_date,
            booking_time=booking.booking_time,
            payment_info=payment_info,
            address=get_salon_address(),
        )

        keyboard = create_inline_keyboard(booking.booking_id)

        print('🔔 DEBUG: Отправка сообщения через Bot API...')
        success = send_telegram_message(
            chat_id,
            message,
            reply_markup=keyboard,
        )
        print(f'🔔 DEBUG: Результат отправки: {success}')

        if not success:
            print('❌ DEBUG: Не удалось отправить сообщение через Bot API')

        return success

    except Exception as e:
        print(f'❌ DEBUG: Критическая ошибка в send_booking_notification: {e}')
        import traceback

        print(f'❌ DEBUG: Трассировка: {traceback.format_exc()}')
        return False


def send_client_notification(booking, notification_type):
    """Отправляет уведомление клиенту выбранным способом."""
    if booking.notification_method == 'telegram':
        print(f'🔔 DEBUG: Отправка Telegram на {booking.client_phone}')
        return send_telegram_notification(booking, notification_type)
    elif booking.notification_method == 'email':
        print('🔔 DEBUG: Выбран Email')
        return send_email_notification(booking, notification_type)
    else:
        print(f'🔔 DEBUG: Неизвестный метод: {booking.notification_method}')
    return False


def send_telegram_notification(booking, notification_type):
    """Отправляет уведомление в Telegram через личный аккаунт."""
    templates = {
        'confirmed': CLIENT_CONFIRMED_TEMPLATE,
        'cancelled': CLIENT_CANCELLED_TEMPLATE,
    }

    if notification_type not in templates:
        print(f'❌ Неизвестный тип уведомления: {notification_type}')
        return False

    message = templates[notification_type].format(
        client_name=booking.client_name,
        procedure_title=booking.procedure.title,
        master_name=booking.master.name,
        master_phone=get_contact_phone(),
        booking_date=booking.booking_date,
        booking_time=booking.booking_time.strftime('%H:%M'),
        address=get_salon_address(),
    )

    print(
        f'🔔 Отправка Telegram на {booking.client_phone}: {notification_type}'
    )

    return send_personal_telegram_message(booking.client_phone, message)


def answer_callback_query(callback_query_id, text):
    """Отправляет ответ на callback query."""
    bot = TelegramBot.objects.filter(is_active=True).first()
    if not bot:
        return False

    url = f'https://api.telegram.org/bot{bot.token}/answerCallbackQuery'
    payload = {'callback_query_id': callback_query_id, 'text': text}

    try:
        response = requests.post(url, json=payload, timeout=5)
        return response.status_code == HTTPStatus.OK
    except Exception:
        return False


def create_reminder_keyboard(booking_id):
    """Создает клавиатуру для подтверждения/отмены напоминания."""
    return {
        'inline_keyboard': [
            [
                {
                    'text': CONFIRM_BUTTON_TEXT,
                    'callback_data': f'reminder_confirm_{booking_id}',
                },
                {
                    'text': CANCEL_BUTTON_TEXT,
                    'callback_data': f'reminder_cancel_{booking_id}',
                },
            ]
        ]
    }


def send_reminder_notification(booking):
    """Отправляет напоминание клиенту."""
    if booking.notification_method == 'telegram':
        return send_telegram_reminder(booking)
    elif booking.notification_method == 'email':
        return send_email_reminder(booking)
    return False


def send_telegram_reminder(booking):
    """Отправляет напоминание в Telegram через ЛИЧНЫЕ сообщения."""
    message = REMINDER_TELEGRAM_TEMPLATE.format(
        client_name=booking.client_name,
        procedure_title=booking.procedure.title,
        master_name=booking.master.name,
        booking_date=booking.booking_date,
        booking_time=booking.booking_time.strftime('%H:%M'),
        address=get_salon_address(),
        master_phone=get_contact_phone(),
    )
    print(f'📤 Отправка личного напоминания на {booking.client_phone}')
    return send_personal_telegram_message(booking.client_phone, message)


def send_email_reminder(booking):
    """Отправляет напоминание по email."""
    if not booking.client_email:
        return False

    message = REMINDER_EMAIL_TEMPLATE.format(
        client_name=booking.client_name,
        procedure_title=booking.procedure.title,
        master_name=booking.master.name,
        booking_date=booking.booking_date,
        booking_time=booking.booking_time.strftime('%H:%M'),
        address=get_salon_address(),
        master_phone=get_contact_phone(),
    )

    try:
        send_mail(
            subject='🔔 Напоминание о записи',
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[booking.client_email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f'DEBUG: Ошибка отправки email напоминания: {str(e)}')
        return False


def send_confirmation_notification(booking):
    """Отправляет подтверждение клиенту."""
    if booking.notification_method == 'telegram':
        message = CONFIRMATION_TELEGRAM_TEMPLATE.format(
            booking_date=booking.booking_date,
            booking_time=booking.booking_time.strftime('%H:%M'),
            address=get_salon_address(),
            master_phone=get_contact_phone(),
        )

        client_chat = ClientChat.objects.filter(
            phone=booking.client_phone
        ).first()
        if client_chat:
            send_telegram_message(client_chat.chat_id, message)


def send_cancellation_notification(booking):
    """Отправляет уведомление об отмене."""
    if booking.notification_method == 'telegram':
        message = CANCELLATION_TELEGRAM_TEMPLATE.format(
            master_phone=get_contact_phone()
        )

        client_chat = ClientChat.objects.filter(
            phone=booking.client_phone
        ).first()
        if client_chat:
            send_telegram_message(client_chat.chat_id, message)
