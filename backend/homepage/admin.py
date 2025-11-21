from django.contrib import admin
from .models import HomePageContent, ContentImage


class ContentImageInline(admin.TabularInline):
    model = ContentImage
    extra = 1
    fields = ['image', 'caption', 'position', 'order']


@admin.register(HomePageContent)
class HomePageContentAdmin(admin.ModelAdmin):
    list_display = ['title', 'price', 'is_active', 'updated_at']
    list_editable = ['is_active', 'price']
    readonly_fields = ['updated_at']
    inlines = [ContentImageInline]

    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'main_description', 'is_active')
        }),
        ('Описание услуги', {
            'fields': ('service_title', 'service_description', 'how_it_works')
        }),
        ('Механизмы и особенности', {
            'fields': ('mechanisms', 'features')
        }),
        ('Проблемы и преимущества', {
            'fields': ('problems', 'advantages')
        }),
        ('Этапы процедуры', {
            'fields': ('stages',)
        }),
        ('Цены', {
            'fields': ('price', 'price_description')
        }),
        ('Системная информация', {
            'fields': ('updated_at',),
            'classes': ('collapse',)
        })
    )
