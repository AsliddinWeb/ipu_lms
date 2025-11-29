# apps/analytics/models.py

from django.db import models
from apps.accounts.models import User
from apps.courses.models import Course, Lesson


class ActivityLog(models.Model):
    """Faollik logi"""

    class ActivityType(models.TextChoices):
        LOGIN = 'login', 'Tizimga kirish'
        LOGOUT = 'logout', 'Tizimdan chiqish'
        VIEW_COURSE = 'view_course', 'Kurs ko\'rish'
        ENROLL_COURSE = 'enroll_course', 'Kursga yozilish'
        VIEW_LESSON = 'view_lesson', 'Dars ko\'rish'
        COMPLETE_LESSON = 'complete_lesson', 'Dars tugatish'
        START_QUIZ = 'start_quiz', 'Test boshlash'
        COMPLETE_QUIZ = 'complete_quiz', 'Test tugatish'

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='activities',
        verbose_name="Foydalanuvchi"
    )
    activity_type = models.CharField(
        max_length=50,
        choices=ActivityType.choices,
        verbose_name="Faollik turi"
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='activities',
        verbose_name="Kurs"
    )
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='activities',
        verbose_name="Dars"
    )

    description = models.TextField(blank=True, verbose_name="Tavsif")
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="IP manzil")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Faollik"
        verbose_name_plural = "Faolliklar"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.get_activity_type_display()}"

    @classmethod
    def log(cls, user, activity_type, course=None, lesson=None, description='', ip_address=None):
        """Faollikni qayd qilish"""
        return cls.objects.create(
            user=user,
            activity_type=activity_type,
            course=course,
            lesson=lesson,
            description=description,
            ip_address=ip_address
        )