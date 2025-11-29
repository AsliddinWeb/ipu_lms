# apps/assessments/models.py

from django.db import models
from django.utils import timezone
from apps.accounts.models import User
from apps.courses.models import Course


class Quiz(models.Model):
    """Test"""
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='quizzes',
        verbose_name="Kurs"
    )
    title = models.CharField(max_length=200, verbose_name="Sarlavha")
    description = models.TextField(blank=True, verbose_name="Tavsif")

    # Sozlamalar
    time_limit_minutes = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Vaqt chegarasi (daqiqa)"
    )
    passing_score = models.PositiveIntegerField(
        default=60,
        verbose_name="O'tish bali (%)"
    )
    attempts_allowed = models.PositiveIntegerField(
        default=1,
        verbose_name="Urinishlar soni"
    )
    shuffle_questions = models.BooleanField(
        default=True,
        verbose_name="Savollarni aralashtirish"
    )
    show_correct_answers = models.BooleanField(
        default=False,
        verbose_name="To'g'ri javoblarni ko'rsatish"
    )

    # Vaqt oralig'i
    available_from = models.DateTimeField(verbose_name="Boshlanish vaqti")
    available_until = models.DateTimeField(verbose_name="Tugash vaqti")

    is_active = models.BooleanField(default=True, verbose_name="Faol")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Test"
        verbose_name_plural = "Testlar"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.course.code} - {self.title}"

    def question_count(self):
        return self.questions.count()

    def total_points(self):
        return self.questions.aggregate(total=models.Sum('points'))['total'] or 0

    def is_available(self):
        now = timezone.now()
        return self.is_active and self.available_from <= now <= self.available_until

    def get_status(self):
        now = timezone.now()
        if now < self.available_from:
            return 'upcoming'
        elif now > self.available_until:
            return 'expired'
        elif self.is_active:
            return 'active'
        return 'inactive'


class Question(models.Model):
    """Savol"""

    class Type(models.TextChoices):
        SINGLE = 'single', 'Bitta to\'g\'ri javob'
        MULTIPLE = 'multiple', 'Ko\'p tanlov'
        TRUE_FALSE = 'true_false', 'To\'g\'ri/Noto\'g\'ri'

    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name='questions',
        verbose_name="Test"
    )
    question_type = models.CharField(
        max_length=20,
        choices=Type.choices,
        default=Type.SINGLE,
        verbose_name="Savol turi"
    )
    text = models.TextField(verbose_name="Savol matni")
    points = models.PositiveIntegerField(default=1, verbose_name="Ball")
    order = models.PositiveIntegerField(default=0, verbose_name="Tartib")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Savol"
        verbose_name_plural = "Savollar"
        ordering = ['order']

    def __str__(self):
        return f"{self.text[:50]}..."

    def correct_answers(self):
        return self.answers.filter(is_correct=True)


class Answer(models.Model):
    """Javob varianti"""
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='answers',
        verbose_name="Savol"
    )
    text = models.CharField(max_length=500, verbose_name="Javob matni")
    is_correct = models.BooleanField(default=False, verbose_name="To'g'ri")
    order = models.PositiveIntegerField(default=0, verbose_name="Tartib")

    class Meta:
        verbose_name = "Javob"
        verbose_name_plural = "Javoblar"
        ordering = ['order']

    def __str__(self):
        return self.text


class QuizAttempt(models.Model):
    """Test urinishi"""
    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name='attempts',
        verbose_name="Test"
    )
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='quiz_attempts',
        verbose_name="Talaba"
    )

    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    score = models.PositiveIntegerField(null=True, blank=True, verbose_name="Ball (%)")
    points_earned = models.PositiveIntegerField(default=0, verbose_name="To'plangan ball")
    points_possible = models.PositiveIntegerField(default=0, verbose_name="Maksimal ball")

    is_passed = models.BooleanField(null=True, verbose_name="O'tdimi")

    class Meta:
        verbose_name = "Test urinishi"
        verbose_name_plural = "Test urinishlari"
        ordering = ['-started_at']

    def __str__(self):
        return f"{self.student.username} - {self.quiz.title}"

    def is_completed(self):
        return self.completed_at is not None

    def time_remaining(self):
        if not self.quiz.time_limit_minutes or self.is_completed():
            return None
        elapsed = timezone.now() - self.started_at
        limit = timezone.timedelta(minutes=self.quiz.time_limit_minutes)
        remaining = limit - elapsed
        if remaining.total_seconds() <= 0:
            return 0
        return int(remaining.total_seconds())

    def calculate_score(self):
        total_points = 0
        earned_points = 0

        for student_answer in self.student_answers.all():
            question = student_answer.question
            total_points += question.points

            correct_answers = set(question.correct_answers().values_list('id', flat=True))
            selected_answers = set(student_answer.selected_answers.values_list('id', flat=True))

            if correct_answers == selected_answers:
                student_answer.is_correct = True
                student_answer.points_earned = question.points
                earned_points += question.points
            else:
                student_answer.is_correct = False
                student_answer.points_earned = 0

            student_answer.save()

        self.points_possible = total_points
        self.points_earned = earned_points
        self.score = int((earned_points / total_points) * 100) if total_points > 0 else 0
        self.is_passed = self.score >= self.quiz.passing_score
        self.completed_at = timezone.now()
        self.save()


class StudentAnswer(models.Model):
    """Talaba javobi"""
    attempt = models.ForeignKey(
        QuizAttempt,
        on_delete=models.CASCADE,
        related_name='student_answers',
        verbose_name="Urinish"
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        verbose_name="Savol"
    )
    selected_answers = models.ManyToManyField(
        Answer,
        blank=True,
        verbose_name="Tanlangan javoblar"
    )

    is_correct = models.BooleanField(null=True, verbose_name="To'g'ri")
    points_earned = models.PositiveIntegerField(default=0, verbose_name="Ball")

    class Meta:
        verbose_name = "Talaba javobi"
        verbose_name_plural = "Talaba javoblari"
        unique_together = ['attempt', 'question']

    def __str__(self):
        return f"{self.attempt.student.username} - {self.question}"


class Grade(models.Model):
    """Yakuniy baho"""
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='grades',
        verbose_name="Talaba"
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='grades',
        verbose_name="Kurs"
    )

    quiz_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name="Test bali"
    )
    attendance_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name="Davomat bali"
    )
    assignment_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name="Topshiriq bali"
    )

    total_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name="Umumiy ball"
    )
    letter_grade = models.CharField(
        max_length=2,
        blank=True,
        verbose_name="Harf baho"
    )

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Baho"
        verbose_name_plural = "Baholar"
        unique_together = ['student', 'course']

    def __str__(self):
        return f"{self.student.username} - {self.course.code} - {self.letter_grade}"

    def calculate_total(self):
        # 50% test, 30% topshiriq, 20% davomat
        self.total_score = (
                float(self.quiz_score) * 0.5 +
                float(self.assignment_score) * 0.3 +
                float(self.attendance_score) * 0.2
        )
        self.letter_grade = self.get_letter_grade()
        self.save()

    def get_letter_grade(self):
        score = float(self.total_score)
        if score >= 90:
            return 'A'
        elif score >= 80:
            return 'B'
        elif score >= 70:
            return 'C'
        elif score >= 60:
            return 'D'
        return 'F'