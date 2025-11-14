from django.contrib import admin
from .models import Category, Procedure


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['title', 'short_description', 'is_active']
    list_editable = ['is_active']
    list_filter = ['is_active']
    search_fields = ['title']


@admin.register(Procedure)
class ProcedureAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'category',
        'short_description',
        'price',
        'is_available',
        'created_at'
    ]
    list_editable = ['is_available']
    list_filter = ['is_available', 'category', 'created_at']
    search_fields = ['title', 'short_description']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Основная информация', {
            'fields': (
                'category',
                'title',
                'short_description',
                'description',
                'image'
            )
        }),
        ('Детали процедуры', {
            'fields': ('price', 'duration', 'is_available')
        }),
        ('Системная информация', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
