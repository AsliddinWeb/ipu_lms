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

    if user.is_admin() or user.is_superuser:
        return render(request, 'accounts/dashboard/admin_dashboard.html')
    elif user.is_teacher():
        return render(request, 'accounts/dashboard/teacher_dashboard.html')
    else:
        return render(request, 'accounts/dashboard/student_dashboard.html')


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