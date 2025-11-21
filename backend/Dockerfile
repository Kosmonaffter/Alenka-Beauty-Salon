FROM python:3.9-slim

WORKDIR /app

# Установка зависимостей системы
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-dev \
    && rm -rf /var/lib/apt/lists/*

# Копирование requirements и установка Python зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование бэкенд приложений
COPY . .

# Создание директорий
RUN mkdir -p /app/staticfiles /app/media

# Сборка статики
RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "django_pro.wsgi:application", "--bind", "0.0.0.0:8000"]