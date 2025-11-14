import asyncio
import os
from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError

load_dotenv()


class TelegramSender:
    def __init__(self, api_id, api_hash, phone):
        self.api_id = api_id
        self.api_hash = api_hash
        self.phone = phone
        self.client = TelegramClient('session_name', api_id, api_hash)

    async def send_message(self, recipient, text):
        try:
            # Используем connect() вместо start() для async with
            await self.client.connect()

            # Авторизация
            if not await self.client.is_user_authorized():
                await self.client.send_code_request(self.phone)
                code = input('Введите код из Telegram: ')
                await self.client.sign_in(self.phone, code)

            # Отправка сообщения
            await self.client.send_message(recipient, text)
            print(f"Сообщение отправлено пользователю: {recipient}")

        except SessionPasswordNeededError:
            print("Требуется двухфакторная аутентификация!")
            password = input("Введите пароль: ")
            await self.client.sign_in(password=password)
            await self.client.send_message(recipient, text)

        except Exception as e:
            print(f"Ошибка: {e}")

    async def disconnect(self):
        await self.client.disconnect()


# Использование
async def main():
    # Получаем переменные из .env как строки
    sender = TelegramSender(
        api_id=os.getenv('API_ID', ''),
        api_hash=os.getenv('API_HASH', ''),
        phone=os.getenv('PHONE', '')  # Ваш номер
    )

    # Отправка сообщения
    await sender.send_message(
        recipient='+79932444875',  # или +79998887766
        text='Повторка Привет! Это сообщение с моего личного аккаунта через Python!'
    )

    await sender.disconnect()

# Запуск
if __name__ == "__main__":
    asyncio.run(main())
