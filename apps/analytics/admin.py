# apps/analytics/admin.py

from django.contrib import admin
from .models import ActivityLog


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'activity_type', 'course', 'lesson', 'ip_address', 'created_at')
    list_filter = ('activity_type', 'created_at', 'course')
    search_fields = ('user__username', 'user__first_name', 'description', 'course__name')
    readonly_fields = ('user', 'activity_type', 'course', 'lesson', 'description', 'ip_address', 'created_at')
    date_hierarchy = 'created_at'
    ordering = ['-created_at']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False