# apps/courses/admin.py

from django.contrib import admin
from .models import Course, Module, Lesson, Enrollment, LessonProgress


class ModuleInline(admin.TabularInline):
    model = Module
    extra = 1
    ordering = ['order']


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1
    ordering = ['order']


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'teacher', 'department', 'credits', 'enrolled_count', 'is_active')
    list_filter = ('is_active', 'department', 'credits')
    search_fields = ('name', 'code', 'teacher__username', 'teacher__first_name')
    list_editable = ('is_active',)

    inlines = [ModuleInline]

    fieldsets = (
        (None, {
            'fields': ('name', 'code', 'description', 'image')
        }),
        ('Bog\'lanishlar', {
            'fields': ('department', 'teacher', 'credits')
        }),
        ('Holat', {
            'fields': ('is_active',)
        }),
    )


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order', 'lesson_count')
    list_filter = ('course',)
    search_fields = ('title', 'course__name')
    ordering = ['course', 'order']

    inlines = [LessonInline]


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'module', 'order', 'duration_minutes', 'is_free')
    list_filter = ('module__course', 'is_free')
    search_fields = ('title', 'module__title', 'module__course__name')
    list_editable = ('order', 'is_free')
    ordering = ['module', 'order']


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'status', 'progress', 'enrolled_at')
    list_filter = ('status', 'course')
    search_fields = ('student__username', 'student__first_name', 'course__name')
    readonly_fields = ('enrolled_at', 'completed_at')

    fieldsets = (
        (None, {
            'fields': ('student', 'course')
        }),
        ('Holat', {
            'fields': ('status', 'progress')
        }),
        ('Sanalar', {
            'fields': ('enrolled_at', 'completed_at')
        }),
    )


@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = ('student', 'lesson', 'is_completed', 'completed_at')
    list_filter = ('is_completed', 'lesson__module__course')
    search_fields = ('student__username', 'lesson__title')
    readonly_fields = ('completed_at',)