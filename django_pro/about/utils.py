from .models import Address


def get_salon_address():
    """Возвращает адрес салона."""
    address = Address.objects.first()
    return address.address if address else 'Адрес не указан'


def get_salon_map():
    """Возвращает HTML код карты."""
    address = Address.objects.first()
    return address.map_embed_code if address and address.map_embed_code else ''
