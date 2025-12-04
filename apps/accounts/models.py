# apps/accounts/models.py

from django.contrib.auth.models import AbstractUser
from django.db import models


class Faculty(models.Model):
    """Fakultet"""
    name = models.CharField(max_length=200, verbose_name="Nomi")
    code = models.CharField(max_length=20, unique=True, verbose_name="Kodi")

    class Meta:
        verbose_name = "Fakultet"
        verbose_name_plural = "Fakultetlar"

    def __str__(self):
        return self.name


class Department(models.Model):
    """Kafedra"""
    name = models.CharField(max_length=200, verbose_name="Nomi")
    faculty = models.ForeignKey(
        Faculty,
        on_delete=models.CASCADE,
        related_name='departments',
        verbose_name="Fakultet"
    )

    class Meta:
        verbose_name = "Kafedra"
        verbose_name_plural = "Kafedralar"

    def __str__(self):
        return self.name


class Group(models.Model):
    """Guruh"""
    name = models.CharField(max_length=50, verbose_name="Nomi")
    faculty = models.ForeignKey(
        Faculty,
        on_delete=models.CASCADE,
        related_name='groups',
        verbose_name="Fakultet"
    )
    year = models.IntegerField(verbose_name="Kurs")

    class Meta:
        verbose_name = "Guruh"
        verbose_name_plural = "Guruhlar"

    def __str__(self):
        return self.name


class User(AbstractUser):
    """Foydalanuvchi"""

    class Role(models.TextChoices):
        STUDENT = 'student', 'Talaba'
        TEACHER = 'teacher', 'O\'qituvchi'
        ADMIN = 'admin', 'Administrator'

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.STUDENT,
        verbose_name="Rol"
    )
    phone = models.CharField(max_length=20, blank=True, verbose_name="Telefon")
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True,
        verbose_name="Rasm"
    )

    class Meta:
        verbose_name = "Foydalanuvchi"
        verbose_name_plural = "Foydalanuvchilar"

    def is_student(self):
        return self.role == self.Role.STUDENT

    def is_teacher(self):
        return self.role == self.Role.TEACHER

    def is_admin(self):
        return self.role == self.Role.ADMIN


class StudentProfile(models.Model):
    """Talaba profili"""
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='student_profile'
    )
    student_id = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Talaba ID"
    )
    faculty = models.ForeignKey(
        Faculty,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Fakultet"
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Guruh"
    )
    enrollment_year = models.IntegerField(verbose_name="O'qishga kirgan yili")

    class Meta:
        verbose_name = "Talaba profili"
        verbose_name_plural = "Talaba profillari"

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.student_id}"


class TeacherProfile(models.Model):
    """O'qituvchi profili"""

    class AcademicDegree(models.TextChoices):
        NONE = '', '-- Tanlang --'
        ACADEMICIAN = 'Академик', 'Akademik'
        DSC_PROFESSOR = 'DSc, Профессор', 'DSc, Professor'
        PROFESSOR = 'Профессор', 'Professor'
        PROFESSOR_VB = 'Профессор в.б.', 'Professor v.b.'
        PHD_DOTSENT = 'PhD, Доцент', 'PhD, Dotsent'
        DOTSENT = 'Доцент', 'Dotsent'
        DOTSENT_VB = 'Доцент в.б.', 'Dotsent v.b.'
        SENIOR_TEACHER = 'Катта ўқитувчи', 'Katta o\'qituvchi'
        ASSISTANT = 'Ассистент, ўқитувчи', 'Assistent, o\'qituvchi'
        ASSISTANT_TRAINEE = 'Ассистент-стажёр', 'Assistent-stajer'


    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='teacher_profile'
    )
    employee_id = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Xodim ID"
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Kafedra"
    )
    academic_degree = models.CharField(
        max_length=50,
        choices=AcademicDegree.choices,
        default=AcademicDegree.NONE,
        blank=True,
        verbose_name="Ilmiy daraja"
    )

    class Meta:
        verbose_name = "O'qituvchi profili"
        verbose_name_plural = "O'qituvchi profillari"

    def __str__(self):
        return f"{self.user.get_full_name()}"