import asyncio
from django.conf import settings
from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError

load_dotenv()


class TelegramSender:
    def __init__(self, api_id=None, api_hash=None, phone=None):
        self.api_id = api_id or settings.API_ID
        self.api_hash = api_hash or settings.API_HASH
        self.phone = phone or settings.PHONE
        self.client = TelegramClient('session_name', self.api_id, self.api_hash)

    async def send_message(self, recipient, text):
        try:
            await self.client.connect()

            if not await self.client.is_user_authorized():
                await self.client.send_code_request(self.phone)
                code = input('Введите код из Telegram: ')
                await self.client.sign_in(self.phone, code)

            await self.client.send_message(recipient, text)
            print(f'✅ Сообщение отправлено пользователю: {recipient}')
            return True

        except SessionPasswordNeededError:
            print('Требуется двухфакторная аутентификация!')
            password = input('Введите пароль: ')
            await self.client.sign_in(password=password)
            await self.client.send_message(recipient, text)
            return True

        except Exception as e:
            print(f'❌ Ошибка отправки сообщения: {e}')
            return False

    def disconnect(self):
        'Закрывает соединение'
        self.client.disconnect()


def send_personal_telegram_message(recipient, text):
    'Синхронная функция для отправки сообщения'

    async def _async_send():
        sender = TelegramSender()
        try:
            return await sender.send_message(recipient, text)
        finally:
            sender.disconnect()

    try:
        return asyncio.run(_async_send())
    except Exception as e:
        print(f'❌ Ошибка в синхронной обертке: {e}')
        return False


async def main():
    sender = TelegramSender()
    try:
        await sender.send_message(
            recipient='+79990000000',
            text='Тестовое сообщение',
        )
    finally:
        sender.disconnect()


if __name__ == '__main__':
    asyncio.run(main())
