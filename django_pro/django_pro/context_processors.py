from django.conf import settings
from about.utils import get_contact_phone, get_legal_address


def contact_info(request):
    """Добавляет контактную информацию в контекст для шаблонов."""
    return {
        'contact_phone': get_contact_phone(),
        'contact_email': getattr(settings, 'DEFAULT_FROM_EMAIL', ''),
        'legal_address': get_legal_address(),
    }
