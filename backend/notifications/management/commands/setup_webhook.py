import requests
from django.core.management.base import BaseCommand
from django.conf import settings
from http import HTTPStatus

from notifications.models import TelegramBot


class Command(BaseCommand):
    """
    Установка вебхука для Telegram бота
    python manage.py setup_webhook.
    """
    help = 'Установка вебхука для Telegram бота'

    def handle(self, *args, **options):
        bot = TelegramBot.objects.filter(is_active=True).first()
        if not bot or not bot.token:
            self.stdout.write('❌ Бот не настроен')
            return

        domain = getattr(settings, 'DOMAIN_NAME', None)
        if not domain:
            self.stdout.write('❌ DOMAIN_NAME не установлен в settings.py')
            return

        webhook_url = f'https://{domain}/notifications/telegram-webhook/'
        url = f'https://api.telegram.org/bot{bot.token}/setWebhook'
        payload = {'url': webhook_url, 'drop_pending_updates': True}

        try:
            response = requests.post(url, json=payload, timeout=10)
            if response.status_code == HTTPStatus.OK:
                result = response.json()
                if result.get('ok'):
                    self.stdout.write('✅ Вебхук установлен')
                    self.stdout.write(f'🔗 URL: {webhook_url}')
                else:
                    error_msg = result.get('description', 'Неизвестная ошибка')
                    self.stdout.write(f'❌ Ошибка: {error_msg}')
            else:
                self.stdout.write(f'❌ HTTP ошибка: {response.status_code}')
        except Exception as e:
            self.stdout.write(f'❌ Ошибка: {e}')
