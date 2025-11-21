from django.core.management.base import BaseCommand
import requests
from django.conf import settings
from notifications.models import TelegramBot
from masters.models import Master


class Command(BaseCommand):
    """
    Создадим команду для полной диагностики
    python manage.py diagnose_bot.
    """

    help = 'Полная диагностика системы бота'

    def handle(self, *args, **options):
        self.stdout.write('🔍 ДИАГНОСТИКА СИСТЕМЫ БОТА')
        self.stdout.write('=' * 50)

        # 1. Проверяем бота в базе
        self.stdout.write('\n1. 📋 Проверка бота в базе данных...')
        bot = TelegramBot.objects.filter(is_active=True).first()
        if not bot:
            self.stdout.write('❌ Бот не найден в базе данных')
            self.stdout.write(
                '💡 Решение: Создайте бота в админке '
                '/admin/notifications/telegrambot/'
            )
            return
        else:
            self.stdout.write('✅ Бот найден в базе')
            self.stdout.write(f'   Название: {bot.name}')
            self.stdout.write(f'   Токен: {"Ест" if bot.token else "НЕТ"}')

        if not bot.token:
            self.stdout.write('❌ Токен бота не установлен')
            self.stdout.write(
                '💡 Решение: Установите TELEGRAM_BOT_TOKEN в настройках'
            )
            return

        # 2. Проверяем API бота
        self.stdout.write('\n2. 🤖 Проверка API бота...')
        url = f'https://api.telegram.org/bot{bot.token}/getMe'
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                bot_info = response.json()
                if bot_info.get('ok'):
                    self.stdout.write('✅ Бот активен в Telegram')
                    self.stdout.write(
                        f'   Имя: {bot_info["result"]["first_name"]}'
                    )
                    self.stdout.write(
                        f'   Username: @{bot_info["result"]["username"]}'
                    )
                else:
                    self.stdout.write('❌ Неверный токен бота')
                    return
            else:
                self.stdout.write(f'❌ Ошибка API: {response.status_code}')
                return
        except Exception as e:
            self.stdout.write(f'❌ Ошибка подключения: {e}')
            return

        # 3. Проверяем мастеров
        self.stdout.write('\n3. 👨‍💼 Проверка мастеров...')
        masters = Master.objects.filter(is_active=True)
        if not masters:
            self.stdout.write('❌ Нет активных мастеров')
        else:
            self.stdout.write(
                f'✅ Найдено {masters.count()} активных мастеров:'
            )
            for master in masters:
                chat_info = (
                    f'Chat ID: {master.telegram_chat_id}'
                    if master.telegram_chat_id
                    else '❌ Chat ID не установлен'
                )
                self.stdout.write(f'   {master.name} - {chat_info}')

        # 4. Проверяем TELEGRAM_ADMIN_CHAT_ID
        self.stdout.write('\n4. 👑 Проверка ADMIN_CHAT_ID...')
        admin_chat_id = getattr(settings, 'TELEGRAM_ADMIN_CHAT_ID', '')
        if admin_chat_id:
            self.stdout.write(f'✅ TELEGRAM_ADMIN_CHAT_ID: {admin_chat_id}')
        else:
            self.stdout.write('❌ TELEGRAM_ADMIN_CHAT_ID не установлен')

        # 5. Проверяем есть ли кому отправлять уведомления
        self.stdout.write('\n5. 📤 Проверка получателей уведомлений...')
        has_recipients = False
        for master in masters:
            if master.telegram_chat_id:
                has_recipients = True
                break

        if admin_chat_id:
            has_recipients = True

        if has_recipients:
            self.stdout.write('✅ Есть получатели для уведомлений')
        else:
            self.stdout.write('❌ НЕТ получателей для уведомлений!')
            self.stdout.write(
                '💡 Решение: Установите telegram_chat_id '
                'мастерам или TELEGRAM_ADMIN_CHAT_ID'
            )

        # 6. Проверяем вебхук
        self.stdout.write('\n6. 🌐 Проверка вебхука...')
        webhook_url = f'https://api.telegram.org/bot{bot.token}/getWebhookInfo'
        try:
            response = requests.get(webhook_url, timeout=10)
            if response.status_code == 200:
                webhook_info = response.json()
                if webhook_info.get('ok'):
                    info = webhook_info['result']
                    if info.get('url'):
                        self.stdout.write(
                            f'✅ Вебхук установлен: {info["url"]}'
                        )
                        self.stdout.write(
                            f'   Ожидает сообщений: '
                            f'{info.get("pending_update_count", 0)}'
                        )
                        if info.get('last_error_message'):
                            self.stdout.write(
                                f'   ❌ Последняя ошибка: '
                                f'{info["last_error_message"]}'
                            )
                    else:
                        self.stdout.write('❌ Вебхук не установлен')
                else:
                    self.stdout.write(
                        '❌ Ошибка получения информации о вебхуке'
                    )
        except Exception as e:
            self.stdout.write(f'❌ Ошибка проверки вебхука: {e}')

        self.stdout.write('\n' + '=' * 50)
        self.stdout.write('📊 ДИАГНОСТИКА ЗАВЕРШЕНА')
