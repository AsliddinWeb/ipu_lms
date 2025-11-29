# apps/attendance/admin.py

from django.contrib import admin
from .models import Session, Attendance


class AttendanceInline(admin.TabularInline):
    model = Attendance
    extra = 0
    readonly_fields = ('marked_at',)


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ('course', 'title', 'session_type', 'date', 'start_time', 'end_time', 'present_count',
                    'absent_count')
    list_filter = ('session_type', 'course', 'date')
    search_fields = ('title', 'course__name', 'course__code')
    date_hierarchy = 'date'
    ordering = ['-date', '-start_time']

    inlines = [AttendanceInline]

    fieldsets = (
        (None, {
            'fields': ('course', 'title', 'session_type')
        }),
        ('Vaqt', {
            'fields': ('date', 'start_time', 'end_time')
        }),
    )


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'session', 'status', 'marked_at')
    list_filter = ('status', 'session__course', 'session__date')
    search_fields = ('student__username', 'student__first_name', 'session__course__name')
    list_editable = ('status',)
    readonly_fields = ('marked_at',)
    ordering = ['-session__date']