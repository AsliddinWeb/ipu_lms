# apps/attendance/models.py

from django.db import models
from apps.accounts.models import User
from apps.courses.models import Course


class Session(models.Model):
    """Dars sessiyasi"""

    class Type(models.TextChoices):
        LECTURE = 'lecture', 'Ma\'ruza'
        SEMINAR = 'seminar', 'Seminar'
        LAB = 'lab', 'Laboratoriya'
        PRACTICE = 'practice', 'Amaliyot'

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='sessions',
        verbose_name="Kurs"
    )
    title = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Mavzu"
    )
    session_type = models.CharField(
        max_length=20,
        choices=Type.choices,
        default=Type.LECTURE,
        verbose_name="Turi"
    )

    date = models.DateField(verbose_name="Sana")
    start_time = models.TimeField(verbose_name="Boshlanish vaqti")
    end_time = models.TimeField(verbose_name="Tugash vaqti")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Sessiya"
        verbose_name_plural = "Sessiyalar"
        ordering = ['-date', '-start_time']

    def __str__(self):
        return f"{self.course.code} - {self.date} ({self.get_session_type_display()})"

    def attendance_count(self):
        return self.attendances.count()

    def present_count(self):
        return self.attendances.filter(status='present').count()

    def absent_count(self):
        return self.attendances.filter(status='absent').count()


class Attendance(models.Model):
    """Davomat"""

    class Status(models.TextChoices):
        PRESENT = 'present', 'Qatnashdi'
        ABSENT = 'absent', 'Qatnashmadi'
        LATE = 'late', 'Kechikdi'
        EXCUSED = 'excused', 'Sababli'

    session = models.ForeignKey(
        Session,
        on_delete=models.CASCADE,
        related_name='attendances',
        verbose_name="Sessiya"
    )
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'student'},
        related_name='attendances',
        verbose_name="Talaba"
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ABSENT,
        verbose_name="Holat"
    )
    notes = models.TextField(blank=True, verbose_name="Izoh")

    marked_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Davomat"
        verbose_name_plural = "Davomatlar"
        unique_together = ['session', 'student']

    def __str__(self):
        return f"{self.student.username} - {self.session} - {self.get_status_display()}"