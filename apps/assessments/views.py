# apps/assessments/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Avg

from .models import Quiz, Question, Answer, QuizAttempt, StudentAnswer, Grade
from .forms import QuizForm, QuestionForm, AnswerFormSet, QuizTakeForm
from apps.courses.models import Course, Enrollment


# ===================== TALABA =====================

@login_required
def quiz_list(request):
    """Talaba uchun testlar ro'yxati"""
    enrollments = Enrollment.objects.filter(
        student=request.user,
        status='active'
    ).values_list('course_id', flat=True)

    quizzes = Quiz.objects.filter(
        course_id__in=enrollments,
        is_active=True
    ).select_related('course')

    # Har bir test uchun urinishlar sonini olish
    quiz_data = []
    for quiz in quizzes:
        attempts = QuizAttempt.objects.filter(
            quiz=quiz,
            student=request.user
        )
        attempts_count = attempts.count()
        best_score = attempts.order_by('-score').first()

        quiz_data.append({
            'quiz': quiz,
            'attempts_count': attempts_count,
            'attempts_left': quiz.attempts_allowed - attempts_count,
            'best_score': best_score.score if best_score else None,
            'is_passed': best_score.is_passed if best_score else None
        })

    return render(request, 'assessments/quiz_list.html', {
        'quiz_data': quiz_data
    })


@login_required
def quiz_detail(request, pk):
    """Test tafsilotlari"""
    quiz = get_object_or_404(Quiz, pk=pk, is_active=True)

    # Yozilganligini tekshirish
    enrollment = Enrollment.objects.filter(
        student=request.user,
        course=quiz.course,
        status='active'
    ).first()

    if not enrollment:
        messages.error(request, 'Bu testni topshirish uchun kursga yoziling!')
        return redirect('courses:detail', pk=quiz.course.pk)

    # Urinishlar
    attempts = QuizAttempt.objects.filter(
        quiz=quiz,
        student=request.user
    ).order_by('-started_at')

    attempts_left = quiz.attempts_allowed - attempts.count()

    # Davom etayotgan urinish bormi?
    ongoing_attempt = attempts.filter(completed_at__isnull=True).first()

    return render(request, 'assessments/quiz_detail.html', {
        'quiz': quiz,
        'attempts': attempts,
        'attempts_left': attempts_left,
        'ongoing_attempt': ongoing_attempt
    })


@login_required
def quiz_start(request, pk):
    """Testni boshlash"""
    quiz = get_object_or_404(Quiz, pk=pk, is_active=True)

    # Yozilganligini tekshirish
    enrollment = Enrollment.objects.filter(
        student=request.user,
        course=quiz.course,
        status='active'
    ).first()

    if not enrollment:
        messages.error(request, 'Bu testni topshirish uchun kursga yoziling!')
        return redirect('courses:detail', pk=quiz.course.pk)

    # Mavjud bo'lganligini tekshirish
    if not quiz.is_available():
        messages.error(request, 'Bu test hozirda mavjud emas!')
        return redirect('assessments:quiz_detail', pk=pk)

    # Urinishlar sonini tekshirish
    attempts_count = QuizAttempt.objects.filter(
        quiz=quiz,
        student=request.user,
        completed_at__isnull=False
    ).count()

    if attempts_count >= quiz.attempts_allowed:
        messages.error(request, 'Urinishlar soni tugagan!')
        return redirect('assessments:quiz_detail', pk=pk)

    # Davom etayotgan urinish bormi?
    ongoing_attempt = QuizAttempt.objects.filter(
        quiz=quiz,
        student=request.user,
        completed_at__isnull=True
    ).first()

    if ongoing_attempt:
        return redirect('assessments:quiz_take', pk=ongoing_attempt.pk)

    # Yangi urinish yaratish
    attempt = QuizAttempt.objects.create(
        quiz=quiz,
        student=request.user
    )

    return redirect('assessments:quiz_take', pk=attempt.pk)


@login_required
def quiz_take(request, pk):
    """Testni topshirish"""
    attempt = get_object_or_404(QuizAttempt, pk=pk, student=request.user)

    # Tugatilganmi?
    if attempt.is_completed():
        return redirect('assessments:quiz_result', pk=pk)

    # Vaqt tugaganmi?
    time_remaining = attempt.time_remaining()
    if time_remaining is not None and time_remaining <= 0:
        attempt.calculate_score()
        messages.warning(request, 'Vaqt tugadi! Test avtomatik yakunlandi.')
        return redirect('assessments:quiz_result', pk=pk)

    quiz = attempt.quiz
    questions = quiz.questions.prefetch_related('answers').all()

    if quiz.shuffle_questions:
        questions = questions.order_by('?')

    if request.method == 'POST':
        # Javoblarni saqlash
        for question in questions:
            field_name = f'question_{question.pk}'
            selected_ids = request.POST.getlist(field_name)

            if selected_ids:
                student_answer, created = StudentAnswer.objects.get_or_create(
                    attempt=attempt,
                    question=question
                )
                student_answer.selected_answers.clear()
                student_answer.selected_answers.add(*selected_ids)

        # Testni yakunlash
        attempt.calculate_score()
        messages.success(request, 'Test yakunlandi!')
        return redirect('assessments:quiz_result', pk=pk)

    return render(request, 'assessments/quiz_take.html', {
        'attempt': attempt,
        'quiz': quiz,
        'questions': questions,
        'time_remaining': time_remaining
    })


@login_required
def quiz_result(request, pk):
    """Test natijasi"""
    attempt = get_object_or_404(QuizAttempt, pk=pk, student=request.user)

    if not attempt.is_completed():
        return redirect('assessments:quiz_take', pk=pk)

    student_answers = attempt.student_answers.select_related(
        'question'
    ).prefetch_related('selected_answers', 'question__answers').all()

    return render(request, 'assessments/quiz_result.html', {
        'attempt': attempt,
        'student_answers': student_answers,
        'show_correct': attempt.quiz.show_correct_answers
    })


@login_required
def gradebook(request):
    """Talaba baholar jadvali"""
    enrollments = Enrollment.objects.filter(
        student=request.user
    ).select_related('course')

    grades_data = []
    for enrollment in enrollments:
        grade, created = Grade.objects.get_or_create(
            student=request.user,
            course=enrollment.course
        )

        # Test balini hisoblash
        attempts = QuizAttempt.objects.filter(
            student=request.user,
            quiz__course=enrollment.course,
            completed_at__isnull=False
        )

        if attempts.exists():
            avg_score = attempts.aggregate(avg=Avg('score'))['avg']
            grade.quiz_score = avg_score or 0
            grade.calculate_total()

        grades_data.append({
            'course': enrollment.course,
            'grade': grade,
            'enrollment': enrollment
        })

    return render(request, 'assessments/gradebook.html', {
        'grades_data': grades_data
    })


# ===================== O'QITUVCHI =====================

@login_required
def teacher_quiz_list(request):
    """O'qituvchi testlari"""
    if not request.user.is_teacher():
        messages.error(request, 'Sizda ruxsat yo\'q!')
        return redirect('accounts:dashboard')

    quizzes = Quiz.objects.filter(
        course__teacher=request.user
    ).select_related('course')

    return render(request, 'assessments/teacher/quiz_list.html', {
        'quizzes': quizzes
    })


@login_required
def teacher_quiz_create(request, course_pk):
    """Test yaratish"""
    course = get_object_or_404(Course, pk=course_pk, teacher=request.user)

    if request.method == 'POST':
        form = QuizForm(request.POST)
        if form.is_valid():
            quiz = form.save(commit=False)
            quiz.course = course
            quiz.save()
            messages.success(request, 'Test yaratildi! Endi savollar qo\'shing.')
            return redirect('assessments:teacher_quiz_detail', pk=quiz.pk)
    else:
        form = QuizForm()

    return render(request, 'assessments/teacher/quiz_form.html', {
        'form': form,
        'course': course,
        'title': 'Yangi test'
    })


@login_required
def teacher_quiz_edit(request, pk):
    """Testni tahrirlash"""
    quiz = get_object_or_404(Quiz, pk=pk, course__teacher=request.user)

    if request.method == 'POST':
        form = QuizForm(request.POST, instance=quiz)
        if form.is_valid():
            form.save()
            messages.success(request, 'Test yangilandi!')
            return redirect('assessments:teacher_quiz_detail', pk=pk)
    else:
        form = QuizForm(instance=quiz)

    return render(request, 'assessments/teacher/quiz_form.html', {
        'form': form,
        'quiz': quiz,
        'course': quiz.course,
        'title': 'Testni tahrirlash'
    })


@login_required
def teacher_quiz_delete(request, pk):
    """Testni o'chirish"""
    quiz = get_object_or_404(Quiz, pk=pk, course__teacher=request.user)

    if request.method == 'POST':
        course_pk = quiz.course.pk
        quiz.delete()
        messages.success(request, 'Test o\'chirildi!')
        return redirect('courses:teacher_course_detail', pk=course_pk)

    return render(request, 'assessments/teacher/quiz_confirm_delete.html', {
        'quiz': quiz
    })


@login_required
def teacher_quiz_detail(request, pk):
    """Test boshqaruvi"""
    quiz = get_object_or_404(Quiz, pk=pk, course__teacher=request.user)
    questions = quiz.questions.prefetch_related('answers').all()

    # Statistika
    attempts = QuizAttempt.objects.filter(quiz=quiz, completed_at__isnull=False)
    stats = {
        'total_attempts': attempts.count(),
        'avg_score': attempts.aggregate(avg=Avg('score'))['avg'] or 0,
        'passed_count': attempts.filter(is_passed=True).count()
    }

    return render(request, 'assessments/teacher/quiz_detail.html', {
        'quiz': quiz,
        'questions': questions,
        'stats': stats
    })


@login_required
def teacher_question_create(request, quiz_pk):
    """Savol qo'shish"""
    quiz = get_object_or_404(Quiz, pk=quiz_pk, course__teacher=request.user)

    if request.method == 'POST':
        form = QuestionForm(request.POST)
        formset = AnswerFormSet(request.POST)

        if form.is_valid() and formset.is_valid():
            question = form.save(commit=False)
            question.quiz = quiz
            question.save()

            formset.instance = question
            formset.save()

            messages.success(request, 'Savol qo\'shildi!')
            return redirect('assessments:teacher_quiz_detail', pk=quiz_pk)
    else:
        last_order = quiz.questions.count()
        form = QuestionForm(initial={'order': last_order})
        formset = AnswerFormSet()

    return render(request, 'assessments/teacher/question_form.html', {
        'form': form,
        'formset': formset,
        'quiz': quiz,
        'title': 'Yangi savol'
    })


@login_required
def teacher_question_edit(request, pk):
    """Savolni tahrirlash"""
    question = get_object_or_404(Question, pk=pk, quiz__course__teacher=request.user)

    if request.method == 'POST':
        form = QuestionForm(request.POST, instance=question)
        formset = AnswerFormSet(request.POST, instance=question)

        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, 'Savol yangilandi!')
            return redirect('assessments:teacher_quiz_detail', pk=question.quiz.pk)
    else:
        form = QuestionForm(instance=question)
        formset = AnswerFormSet(instance=question)

    return render(request, 'assessments/teacher/question_form.html', {
        'form': form,
        'formset': formset,
        'question': question,
        'quiz': question.quiz,
        'title': 'Savolni tahrirlash'
    })


@login_required
def teacher_question_delete(request, pk):
    """Savolni o'chirish"""
    question = get_object_or_404(Question, pk=pk, quiz__course__teacher=request.user)

    if request.method == 'POST':
        quiz_pk = question.quiz.pk
        question.delete()
        messages.success(request, 'Savol o\'chirildi!')
        return redirect('assessments:teacher_quiz_detail', pk=quiz_pk)

    return render(request, 'assessments/teacher/question_confirm_delete.html', {
        'question': question
    })


@login_required
def teacher_quiz_results(request, pk):
    """Test natijalari"""
    quiz = get_object_or_404(Quiz, pk=pk, course__teacher=request.user)

    attempts = QuizAttempt.objects.filter(
        quiz=quiz,
        completed_at__isnull=False
    ).select_related('student').order_by('-completed_at')

    return render(request, 'assessments/teacher/quiz_results.html', {
        'quiz': quiz,
        'attempts': attempts
    })