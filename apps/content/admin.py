# apps/content/admin.py

from django.contrib import admin
from .models import Material


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'lesson', 'material_type', 'get_file_size_display', 'download_count',
                    'is_active', 'created_at')
    list_filter = ('material_type', 'is_active', 'course', 'created_at')
    search_fields = ('title', 'description', 'course__name', 'course__code')
    list_editable = ('is_active',)
    readonly_fields = ('file_size', 'download_count', 'created_at', 'updated_at')
    ordering = ['-created_at']

    fieldsets = (
        (None, {
            'fields': ('course', 'lesson', 'title', 'description')
        }),
        ('Fayl', {
            'fields': ('material_type', 'file', 'url')
        }),
        ('Statistika', {
            'fields': ('file_size', 'download_count', 'is_active')
        }),
        ('Vaqt', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )