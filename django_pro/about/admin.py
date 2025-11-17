from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import Address


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    """Админка для адресов."""

    list_display = [
        'address',
        'is_legal_address',
        'is_display_address',
        'has_map_display',
    ]
    list_editable = ['is_legal_address', 'is_display_address']
    fields = [
        'address',
        'is_legal_address',
        'is_display_address',
        'map_embed_code',
        'map_preview',
    ]
    readonly_fields = ['map_preview']

    @admin.display(description='Юр. адрес', boolean=True)
    def is_legal_address_display(self, obj):
        return obj.is_legal_address

    @admin.display(description='Для отображения', boolean=True)
    def is_display_address_display(self, obj):
        return obj.is_display_address

    @admin.display(description='Есть карта')
    def has_map_display(self, obj):
        return '✅' if obj.has_map() else '❌'

    @admin.display(description='Предпросмотр карты')
    def map_preview(self, obj):
        if obj.map_embed_code:
            return mark_safe(
                f'''
                <div style="margin-top: 10px;">
                    <h4>Предпросмотр карты:</h4>
                    <div style="border: 1px solid #ccc;
                        padding: 10px;
                        border-radius: 5px;">
                        {obj.map_embed_code}
                    </div>
                </div>
                '''
            )
        return 'Карта не настроена'
