# apps/main/views.py

from django.shortcuts import render, redirect
from apps.courses.models import Course
from apps.accounts.models import User, Faculty


def landing_page(request):
    """Landing page"""

    # Statistika
    total_courses = Course.objects.filter(is_active=True).count()
    total_students = User.objects.filter(role='student').count()
    total_teachers = User.objects.filter(role='teacher').count()
    total_faculties = Faculty.objects.count()

    # Mashhur kurslar
    popular_courses = Course.objects.filter(is_active=True).order_by('-created_at')[:6]

    context = {
        'total_courses': total_courses,
        'total_students': total_students,
        'total_teachers': total_teachers,
        'total_faculties': total_faculties,
        'popular_courses': popular_courses,
    }
    return render(request, 'main/landing.html', context)


def about_page(request):
    """Biz haqimizda"""
    return render(request, 'main/about.html')


def contact_page(request):
    """Bog'lanish"""
    if request.method == 'POST':
        # Kontakt formasi logikasi
        pass
    return render(request, 'main/contact.html')