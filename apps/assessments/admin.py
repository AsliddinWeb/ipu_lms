# apps/assessments/admin.py

from django.contrib import admin
from .models import Quiz, Question, Answer, QuizAttempt, StudentAnswer, Grade


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 4
    ordering = ['order']


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1
    ordering = ['order']
    show_change_link = True


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'question_count', 'passing_score', 'attempts_allowed', 'is_active', 'get_status')
    list_filter = ('is_active', 'course', 'created_at')
    search_fields = ('title', 'course__name', 'course__code')
    list_editable = ('is_active',)

    inlines = [QuestionInline]

    fieldsets = (
        (None, {
            'fields': ('course', 'title', 'description')
        }),
        ('Sozlamalar', {
            'fields': ('time_limit_minutes', 'passing_score', 'attempts_allowed', 'shuffle_questions',
                       'show_correct_answers')
        }),
        ('Vaqt oralig\'i', {
            'fields': ('available_from', 'available_until')
        }),
        ('Holat', {
            'fields': ('is_active',)
        }),
    )

    def get_status(self, obj):
        status = obj.get_status()
        status_display = {
            'upcoming': '🕐 Kutilmoqda',
            'active': '✅ Faol',
            'expired': '⏰ Tugagan',
            'inactive': '❌ Faol emas'
        }
        return status_display.get(status, status)

    get_status.short_description = 'Holat'


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text_short', 'quiz', 'question_type', 'points', 'order')
    list_filter = ('question_type', 'quiz__course', 'quiz')
    search_fields = ('text', 'quiz__title')
    ordering = ['quiz', 'order']

    inlines = [AnswerInline]

    def text_short(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text

    text_short.short_description = 'Savol'


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('text', 'question', 'is_correct', 'order')
    list_filter = ('is_correct', 'question__quiz')
    search_fields = ('text', 'question__text')
    list_editable = ('is_correct', 'order')


class StudentAnswerInline(admin.TabularInline):
    model = StudentAnswer
    extra = 0
    readonly_fields = ('question', 'is_correct', 'points_earned')
    can_delete = False


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ('student', 'quiz', 'score', 'is_passed', 'started_at', 'completed_at')
    list_filter = ('is_passed', 'quiz__course', 'quiz')
    search_fields = ('student__username', 'student__first_name', 'quiz__title')
    readonly_fields = ('started_at', 'completed_at', 'score', 'points_earned', 'points_possible', 'is_passed')
    ordering = ['-started_at']

    inlines = [StudentAnswerInline]


@admin.register(StudentAnswer)
class StudentAnswerAdmin(admin.ModelAdmin):
    list_display = ('attempt', 'question', 'is_correct', 'points_earned')
    list_filter = ('is_correct', 'attempt__quiz')
    search_fields = ('attempt__student__username', 'question__text')


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'quiz_score', 'attendance_score', 'assignment_score', 'total_score',
                    'letter_grade')
    list_filter = ('letter_grade', 'course')
    search_fields = ('student__username', 'student__first_name', 'course__name')
    readonly_fields = ('updated_at',)

    fieldsets = (
        (None, {
            'fields': ('student', 'course')
        }),
        ('Ballar', {
            'fields': ('quiz_score', 'attendance_score', 'assignment_score')
        }),
        ('Yakuniy', {
            'fields': ('total_score', 'letter_grade')
        }),
    )