from django.shortcuts import render
from .models import HomePageContent


def index(request):
    """Шаблон главной страницы."""
    content = HomePageContent.objects.filter(is_active=True).first()

    if not content:
        content = HomePageContent.objects.create(
            title="Добро пожаловать!",
            main_description="Кабинет аппаратного массажа АлЁнкА",
            service_title="Массаж R-sleek – коррекция фигуры",
            price=8000.00,
        )

    context = {"content": content}
    return render(request, "homepage/index.html", context)
