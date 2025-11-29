# apps/accounts/views.py

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.urls import reverse_lazy

from .forms import (
    LoginForm,
    StudentRegisterForm,
    TeacherRegisterForm,
    UserUpdateForm,
    StudentProfileForm,
    TeacherProfileForm
)
from .models import StudentProfile, TeacherProfile


class CustomLoginView(LoginView):
    """Login view"""
    form_class = LoginForm
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('accounts:dashboard')

    def form_invalid(self, form):
        messages.error(self.request, 'Login yoki parol noto\'g\'ri!')
        return super().form_invalid(form)


def logout_view(request):
    """Logout view"""
    logout(request)
    messages.success(request, 'Tizimdan chiqdingiz.')
    return redirect('accounts:login')


def register_student(request):
    """Talaba ro'yxatdan o'tish"""
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')

    if request.method == 'POST':
        form = StudentRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Ro\'yxatdan o\'tdingiz! Profilingizni to\'ldiring.')
            return redirect('accounts:profile')
    else:
        form = StudentRegisterForm()

    return render(request, 'accounts/register.html', {
        'form': form,
        'user_type': 'student'
    })


def register_teacher(request):
    """O'qituvchi ro'yxatdan o'tish"""
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')

    if request.method == 'POST':
        form = TeacherRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Ro\'yxatdan o\'tdingiz! Profilingizni to\'ldiring.')
            return redirect('accounts:profile')
    else:
        form = TeacherRegisterForm()

    return render(request, 'accounts/register.html', {
        'form': form,
        'user_type': 'teacher'
    })

@login_required
def dashboard(request):
    """Dashboard - rolga qarab yo'naltirish"""
    user = request.user

    if user.is_admin():
        from apps.accounts.models import User, Faculty, Department
        from apps.courses.models import Course, Enrollment
        from apps.assessments.models import Quiz, QuizAttempt
        from apps.attendance.models import Session
        from apps.analytics.models import ActivityLog
        from django.utils import timezone
        from datetime import timedelta

        # Umumiy statistika
        total_students = User.objects.filter(role='student').count()
        total_teachers = User.objects.filter(role='teacher').count()
        total_courses = Course.objects.count()
        total_faculties = Faculty.objects.count()

        # Faol kurslar
        active_courses = Course.objects.filter(is_active=True).count()

        # Bugungi faollik
        today = timezone.now().date()
        today_start = timezone.make_aware(timezone.datetime.combine(today, timezone.datetime.min.time()))
        today_logins = ActivityLog.objects.filter(
            activity_type='login',
            created_at__gte=today_start
        ).count()

        # So'nggi ro'yxatdan o'tganlar
        recent_users = User.objects.order_by('-date_joined')[:5]

        # So'nggi kurslar
        recent_courses = Course.objects.order_by('-created_at')[:5]

        # So'nggi faolliklar
        recent_activities = ActivityLog.objects.select_related('user', 'course')[:10]

        # Haftalik statistika
        week_ago = timezone.now() - timedelta(days=7)
        weekly_enrollments = Enrollment.objects.filter(enrolled_at__gte=week_ago).count()
        weekly_quiz_attempts = QuizAttempt.objects.filter(
            completed_at__gte=week_ago,
            completed_at__isnull=False
        ).count()

        context = {
            'total_students': total_students,
            'total_teachers': total_teachers,
            'total_courses': total_courses,
            'total_faculties': total_faculties,
            'active_courses': active_courses,
            'today_logins': today_logins,
            'recent_users': recent_users,
            'recent_courses': recent_courses,
            'recent_activities': recent_activities,
            'weekly_enrollments': weekly_enrollments,
            'weekly_quiz_attempts': weekly_quiz_attempts,
        }
        return render(request, 'accounts/dashboard/admin_dashboard.html', context)

    elif user.is_teacher():
        from apps.courses.models import Course, Enrollment
        from apps.assessments.models import Quiz, QuizAttempt
        from apps.attendance.models import Session
        from django.utils import timezone
        from django.db.models import Count

        # Fanlarim
        courses = Course.objects.filter(teacher=user)
        total_courses = courses.count()

        # Talabalar soni
        total_students = Enrollment.objects.filter(
            course__teacher=user,
            status='active'
        ).values('student').distinct().count()

        # Testlar soni
        total_quizzes = Quiz.objects.filter(course__teacher=user).count()

        # Bugungi darslar
        today = timezone.now().date()
        today_sessions = Session.objects.filter(
            course__teacher=user,
            date=today
        ).select_related('course').order_by('start_time')

        # So'nggi test natijalari
        recent_attempts = QuizAttempt.objects.filter(
            quiz__course__teacher=user,
            completed_at__isnull=False
        ).select_related('student', 'quiz').order_by('-completed_at')[:5]

        context = {
            'courses': courses[:5],
            'total_courses': total_courses,
            'total_students': total_students,
            'total_quizzes': total_quizzes,
            'today_sessions': today_sessions,
            'today_sessions_count': today_sessions.count(),
            'recent_attempts': recent_attempts,
        }
        return render(request, 'accounts/dashboard/teacher_dashboard.html', context)

    else:
        from apps.courses.models import Enrollment, LessonProgress
        from apps.assessments.models import Quiz, QuizAttempt
        from apps.attendance.models import Attendance
        from apps.analytics.models import ActivityLog
        from django.db.models import Avg
        from django.utils import timezone

        # Kurslarim
        enrollments = Enrollment.objects.filter(
            student=user,
            status='active'
        ).select_related('course')
        total_courses = enrollments.count()

        # Tugatilgan darslar
        completed_lessons = LessonProgress.objects.filter(
            student=user,
            is_completed=True
        ).count()

        # Testlar
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

        # Yaqinlashayotgan testlar
        now = timezone.now()
        upcoming_quizzes = Quiz.objects.filter(
            course__enrollments__student=user,
            course__enrollments__status='active',
            is_active=True,
            available_from__lte=now,
            available_until__gte=now
        ).select_related('course')[:5]

        # So'nggi faollik
        recent_activities = ActivityLog.objects.filter(user=user)[:5]

        context = {
            'enrollments': enrollments[:5],
            'total_courses': total_courses,
            'completed_lessons': completed_lessons,
            'total_quizzes': total_quizzes,
            'avg_score': avg_score,
            'attendance_percentage': attendance_percentage,
            'upcoming_quizzes': upcoming_quizzes,
            'recent_activities': recent_activities,
        }
        return render(request, 'accounts/dashboard/student_dashboard.html', context)


@login_required
def profile(request):
    """Profil ko'rish va tahrirlash"""
    user = request.user
    profile_form = None
    profile_instance = None

    # Profilni olish yoki yaratish
    if user.is_student():
        profile_instance, created = StudentProfile.objects.get_or_create(
            user=user,
            defaults={'student_id': f'STU{user.id}', 'enrollment_year': 2024}
        )
        profile_form_class = StudentProfileForm
    elif user.is_teacher():
        profile_instance, created = TeacherProfile.objects.get_or_create(
            user=user,
            defaults={'employee_id': f'EMP{user.id}'}
        )
        profile_form_class = TeacherProfileForm
    else:
        profile_form_class = None

    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, request.FILES, instance=user)

        if profile_form_class:
            profile_form = profile_form_class(request.POST, instance=profile_instance)

            if user_form.is_valid() and profile_form.is_valid():
                user_form.save()
                profile_form.save()
                messages.success(request, 'Profil yangilandi!')
                return redirect('accounts:profile')
        else:
            if user_form.is_valid():
                user_form.save()
                messages.success(request, 'Profil yangilandi!')
                return redirect('accounts:profile')
    else:
        user_form = UserUpdateForm(instance=user)
        if profile_form_class:
            profile_form = profile_form_class(instance=profile_instance)

    return render(request, 'accounts/profile.html', {
        'user_form': user_form,
        'profile_form': profile_form,
    })