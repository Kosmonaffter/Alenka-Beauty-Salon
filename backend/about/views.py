from django.shortcuts import render

from .utils import get_salon_address, get_salon_map


def info(request):
    return render(
        request,
        'about/info.html',
        {
            'salon_address': get_salon_address(),
            'salon_map': get_salon_map(),
        }
    )
