from django.shortcuts import render, get_object_or_404

from .models import Procedure


def product_list(request):
    """Список всех процедур"""
    procedures = Procedure.objects.filter(
        is_available=True,
        category__is_active=True
    )

    context = {
        'procedures': procedures
    }
    return render(request, 'catalog/product_list.html', context)


def product_detail(request, pk):
    """Детальная страница процедуры"""
    procedure = get_object_or_404(
        Procedure,
        pk=pk,
        is_available=True,
        category__is_active=True
    )

    context = {
        'procedure': procedure
    }
    return render(request, 'catalog/product_detail.html', context)
