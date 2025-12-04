# apps/courses/models.py

from django.db import models
from apps.accounts.models import User, Department
import re


class Course(models.Model):
    """Kurs/Fan"""
    name = models.CharField(max_length=200, verbose_name="Nomi")
    code = models.CharField(max_length=20, unique=True, verbose_name="Kodi")
    description = models.TextField(blank=True, verbose_name="Tavsif")
    image = models.ImageField(
        upload_to='courses/',
        blank=True,
        null=True,
        verbose_name="Rasm"
    )

    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='courses',
        verbose_name="Kafedra"
    )
    teacher = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        limit_choices_to={'role': 'teacher'},
        related_name='teaching_courses',
        verbose_name="O'qituvchi"
    )

    credits = models.PositiveIntegerField(default=3, verbose_name="Kreditlar")
    is_active = models.BooleanField(default=True, verbose_name="Faol")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Kurs"
        verbose_name_plural = "Kurslar"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.code} - {self.name}"

    def enrolled_count(self):
        return self.enrollments.filter(status='active').count()

    def module_count(self):
        return self.modules.count()

    def lesson_count(self):
        return Lesson.objects.filter(module__course=self).count()


class Module(models.Model):
    """Modul"""
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='modules',
        verbose_name="Kurs"
    )
    title = models.CharField(max_length=200, verbose_name="Sarlavha")
    description = models.TextField(blank=True, verbose_name="Tavsif")
    order = models.PositiveIntegerField(default=0, verbose_name="Tartib")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Modul"
        verbose_name_plural = "Modullar"
        ordering = ['order']

    def __str__(self):
        return f"{self.course.code} - {self.title}"

    def lesson_count(self):
        return self.lessons.count()


class Lesson(models.Model):
    """Dars"""
    module = models.ForeignKey(
        Module,
        on_delete=models.CASCADE,
        related_name='lessons',
        verbose_name="Modul"
    )
    title = models.CharField(max_length=200, verbose_name="Sarlavha")
    content = models.TextField(verbose_name="Kontent")
    video_url = models.URLField(blank=True, verbose_name="Video URL")
    duration_minutes = models.PositiveIntegerField(default=0, verbose_name="Davomiylik (min)")
    order = models.PositiveIntegerField(default=0, verbose_name="Tartib")

    is_free = models.BooleanField(default=False, verbose_name="Bepul")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Dars"
        verbose_name_plural = "Darslar"
        ordering = ['order']

    def __str__(self):
        return self.title

    @property
    def video_embed_url(self):
        """YouTube URL ni embed formatga o'girish"""
        if not self.video_url:
            return ''

        url = self.video_url

        # youtube.com/watch?v=VIDEO_ID
        match = re.search(r'youtube\.com/watch\?v=([a-zA-Z0-9_-]+)', url)
        if match:
            return f'https://www.youtube.com/embed/{match.group(1)}'

        # youtu.be/VIDEO_ID
        match = re.search(r'youtu\.be/([a-zA-Z0-9_-]+)', url)
        if match:
            return f'https://www.youtube.com/embed/{match.group(1)}'

        # Agar allaqachon embed formatda bo'lsa
        if 'youtube.com/embed/' in url:
            return url

        return url


class Enrollment(models.Model):
    """Kursga yozilish"""

    class Status(models.TextChoices):
        ACTIVE = 'active', 'Faol'
        COMPLETED = 'completed', 'Tugatilgan'
        DROPPED = 'dropped', 'Chiqib ketgan'

    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'student'},
        related_name='enrollments',
        verbose_name="Talaba"
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='enrollments',
        verbose_name="Kurs"
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
        verbose_name="Holat"
    )
    progress = models.PositiveIntegerField(default=0, verbose_name="Progress (%)")

    enrolled_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Yozilish"
        verbose_name_plural = "Yozilishlar"
        unique_together = ['student', 'course']

    def __str__(self):
        return f"{self.student.username} - {self.course.name}"

    def update_progress(self):
        total_lessons = self.course.lesson_count()
        if total_lessons == 0:
            self.progress = 0
        else:
            completed = LessonProgress.objects.filter(
                student=self.student,
                lesson__module__course=self.course,
                is_completed=True
            ).count()
            self.progress = int((completed / total_lessons) * 100)
        self.save()


class LessonProgress(models.Model):
    """Dars progressi"""
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='lesson_progress',
        verbose_name="Talaba"
    )
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name='progress',
        verbose_name="Dars"
    )

    is_completed = models.BooleanField(default=False, verbose_name="Tugatilgan")
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Dars progressi"
        verbose_name_plural = "Dars progresslari"
        unique_together = ['student', 'lesson']

    def __str__(self):
        return f"{self.student.username} - {self.lesson.title}"
