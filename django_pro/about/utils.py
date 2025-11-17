from .models import Address


def get_salon_address():
    """Возвращает адрес салона для отображения на страницах."""
    address = Address.objects.filter(is_display_address=True).first()
    if not address:
        address = Address.objects.first()
    return address.address if address else 'Адрес не указан'


def get_salon_map():
    """Возвращает HTML код карты для адреса отображения."""
    address = Address.objects.filter(is_display_address=True).first()
    if not address:
        address = Address.objects.first()
    return address.map_embed_code if address and address.map_embed_code else ''


def get_legal_address():
    """Возвращает юридический адрес для согласий и документов."""
    address = Address.objects.filter(is_legal_address=True).first()
    if not address:
        address = Address.objects.filter(is_display_address=True).first()
        if not address:
            address = Address.objects.first()
    return address.address if address else 'Адрес не указан'


def get_legal_address_object():
    """Возвращает объект юридического адреса."""
    address = Address.objects.filter(is_legal_address=True).first()
    if not address:
        address = Address.objects.filter(is_display_address=True).first()
        if not address:
            address = Address.objects.first()
    return address
