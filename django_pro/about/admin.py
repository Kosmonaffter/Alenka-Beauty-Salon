from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import Address


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    """Админка для бронирований."""

    list_display = ['address', 'has_map_display']
    fields = ['address', 'map_embed_code', 'map_preview']
    readonly_fields = ['map_preview']

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
