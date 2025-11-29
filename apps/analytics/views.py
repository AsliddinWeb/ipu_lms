# apps/analytics/views.py

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Avg, Q
from django.utils import timezone
from datetime import timedelta

from .models import ActivityLog
from apps.courses.models import Course, Enrollment, LessonProgress
from apps.assessments.models import QuizAttempt, Grade
from apps.attendance.models import Attendance


# ===================== TALABA =====================

@login_required
def student_stats(request):
    """Talaba statistikasi"""
    user = request.user

    # Umumiy statistika
    enrollments = Enrollment.objects.filter(student=user, status='active')
    total_courses = enrollments.count()

    completed_lessons = LessonProgress.objects.filter(
        student=user,
        is_completed=True
    ).count()

    quiz_attempts = QuizAttempt.objects.filter(
        student=user,
        completed_at__isnull=False
    )
    total_quizzes = quiz_attempts.count()
    avg_score = quiz_attempts.aggregate(avg=Avg('score'))['avg'] or 0

    # Davomat
    total_attendance = Attendance.objects.filter(student=user).count()
    present_attendance = Attendance.objects.filter(
        student=user,
        status__in=['present', 'late', 'excused']
    ).count()
    attendance_percentage = int((present_attendance / total_attendance) * 100) if total_attendance > 0 else 0

    # So'nggi faolliklar
    recent_activities = ActivityLog.objects.filter(user=user)[:10]

    # Kurslar bo'yicha progress
    course_progress = []
    for enrollment in enrollments:
        course = enrollment.course
        total_lessons = course.lesson_count()
        completed = LessonProgress.objects.filter(
            student=user,
            lesson__module__course=course,
            is_completed=True
        ).count()
        progress = int((completed / total_lessons) * 100) if total_lessons > 0 else 0

        # Kurs bahosi
        grade = Grade.objects.filter(student=user, course=course).first()

        course_progress.append({
            'course': course,
            'total_lessons': total_lessons,
            'completed_lessons': completed,
            'progress': progress,
            'grade': grade
        })

    # Haftalik faollik
    week_ago = timezone.now() - timedelta(days=7)
    weekly_activities = ActivityLog.objects.filter(
        user=user,
        created_at__gte=week_ago
    ).values('activity_type').annotate(count=Count('id'))

    return render(request, 'analytics/student_stats.html', {
        'total_courses': total_courses,
        'completed_lessons': completed_lessons,
        'total_quizzes': total_quizzes,
        'avg_score': avg_score,
        'attendance_percentage': attendance_percentage,
        'recent_activities': recent_activities,
        'course_progress': course_progress,
        'weekly_activities': weekly_activities
    })


# ===================== O'QITUVCHI =====================

@login_required
def teacher_course_analytics(request, course_pk):
    """Kurs statistikasi"""
    if not request.user.is_teacher():
        messages.error(request, 'Sizda ruxsat yo\'q!')
        return redirect('accounts:dashboard')

    course = get_object_or_404(Course, pk=course_pk, teacher=request.user)

    # Umumiy statistika
    total_students = Enrollment.objects.filter(course=course, status='active').count()
    total_lessons = course.lesson_count()
    total_quizzes = course.quizzes.count()

    # O'rtacha progress
    enrollments = Enrollment.objects.filter(course=course, status='active')
    avg_progress = enrollments.aggregate(avg=Avg('progress'))['avg'] or 0

    # Test statistikasi
    quiz_attempts = QuizAttempt.objects.filter(
        quiz__course=course,
        completed_at__isnull=False
    )
    avg_quiz_score = quiz_attempts.aggregate(avg=Avg('score'))['avg'] or 0
    passed_quizzes = quiz_attempts.filter(is_passed=True).count()
    total_attempts = quiz_attempts.count()
    pass_rate = int((passed_quizzes / total_attempts) * 100) if total_attempts > 0 else 0

    # Davomat statistikasi
    total_sessions = course.sessions.count()
    attendances = Attendance.objects.filter(session__course=course)
    present_count = attendances.filter(status='present').count()
    total_attendance = attendances.count()
    attendance_rate = int((present_count / total_attendance) * 100) if total_attendance > 0 else 0

    # Eng faol talabalar
    active_students = Enrollment.objects.filter(
        course=course,
        status='active'
    ).select_related('student').order_by('-progress')[:5]

    # So'nggi faolliklar
    recent_activities = ActivityLog.objects.filter(course=course)[:10]

    return render(request, 'analytics/teacher/course_analytics.html', {
        'course': course,
        'total_students': total_students,
        'total_lessons': total_lessons,
        'total_quizzes': total_quizzes,
        'avg_progress': avg_progress,
        'avg_quiz_score': avg_quiz_score,
        'pass_rate': pass_rate,
        'total_sessions': total_sessions,
        'attendance_rate': attendance_rate,
        'active_students': active_students,
        'recent_activities': recent_activities
    })


@login_required
def teacher_student_progress(request, course_pk, student_pk):
    """Talaba progressi"""
    if not request.user.is_teacher():
        messages.error(request, 'Sizda ruxsat yo\'q!')
        return redirect('accounts:dashboard')

    course = get_object_or_404(Course, pk=course_pk, teacher=request.user)

    enrollment = get_object_or_404(
        Enrollment,
        course=course,
        student_id=student_pk,
        status='active'
    )
    student = enrollment.student

    # Dars progressi
    total_lessons = course.lesson_count()
    completed_lessons = LessonProgress.objects.filter(
        student=student,
        lesson__module__course=course,
        is_completed=True
    ).count()
    lesson_progress = int((completed_lessons / total_lessons) * 100) if total_lessons > 0 else 0

    # Test natijalari
    quiz_attempts = QuizAttempt.objects.filter(
        student=student,
        quiz__course=course,
        completed_at__isnull=False
    ).select_related('quiz').order_by('-completed_at')

    avg_quiz_score = quiz_attempts.aggregate(avg=Avg('score'))['avg'] or 0

    # Davomat
    attendances = Attendance.objects.filter(
        student=student,
        session__course=course
    ).select_related('session').order_by('-session__date')

    total_sessions = course.sessions.count()
    present_count = attendances.filter(status__in=['present', 'late', 'excused']).count()
    attendance_rate = int((present_count / total_sessions) * 100) if total_sessions > 0 else 0

    # Baho
    grade = Grade.objects.filter(student=student, course=course).first()

    # Faollik
    activities = ActivityLog.objects.filter(
        user=student,
        course=course
    )[:10]

    return render(request, 'analytics/teacher/student_progress.html', {
        'course': course,
        'student': student,
        'enrollment': enrollment,
        'total_lessons': total_lessons,
        'completed_lessons': completed_lessons,
        'lesson_progress': lesson_progress,
        'quiz_attempts': quiz_attempts,
        'avg_quiz_score': avg_quiz_score,
        'attendances': attendances,
        'attendance_rate': attendance_rate,
        'grade': grade,
        'activities': activities
    })