# apps/courses/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone

from .models import Course, Module, Lesson, Enrollment, LessonProgress
from .forms import CourseForm, ModuleForm, LessonForm


# ===================== UMUMIY =====================

def course_list(request):
    """Barcha kurslar ro'yxati"""
    courses = Course.objects.filter(is_active=True).select_related('teacher', 'department')

    # Qidiruv
    query = request.GET.get('q')
    if query:
        courses = courses.filter(
            Q(name__icontains=query) |
            Q(code__icontains=query) |
            Q(description__icontains=query)
        )

    # Kafedra bo'yicha filter
    department = request.GET.get('department')
    if department:
        courses = courses.filter(department_id=department)

    return render(request, 'courses/course_list.html', {
        'courses': courses,
        'query': query
    })


def course_detail(request, pk):
    """Kurs tafsilotlari"""
    course = get_object_or_404(Course, pk=pk, is_active=True)
    modules = course.modules.prefetch_related('lessons').all()

    # Foydalanuvchi yozilganmi?
    enrollment = None
    if request.user.is_authenticated and request.user.is_student():
        enrollment = Enrollment.objects.filter(
            student=request.user,
            course=course
        ).first()

    return render(request, 'courses/course_detail.html', {
        'course': course,
        'modules': modules,
        'enrollment': enrollment
    })


@login_required
def course_enroll(request, pk):
    """Kursga yozilish"""
    course = get_object_or_404(Course, pk=pk, is_active=True)

    if not request.user.is_student():
        messages.error(request, 'Faqat talabalar kursga yozilishi mumkin!')
        return redirect('courses:detail', pk=pk)

    # Allaqachon yozilganmi?
    enrollment, created = Enrollment.objects.get_or_create(
        student=request.user,
        course=course,
        defaults={'status': 'active'}
    )

    if created:
        messages.success(request, f'"{course.name}" kursiga muvaffaqiyatli yozildingiz!')
    else:
        messages.info(request, 'Siz allaqachon bu kursga yozilgansiz.')

    return redirect('courses:detail', pk=pk)


@login_required
def course_unenroll(request, pk):
    """Kursdan chiqish"""
    course = get_object_or_404(Course, pk=pk)

    enrollment = Enrollment.objects.filter(
        student=request.user,
        course=course
    ).first()

    if enrollment:
        enrollment.delete()
        messages.success(request, f'"{course.name}" kursidan chiqdingiz.')

    return redirect('courses:detail', pk=pk)


# ===================== TALABA =====================

@login_required
def my_courses(request):
    """Mening kurslarim (Talaba)"""
    enrollments = Enrollment.objects.filter(
        student=request.user,
        status='active'
    ).select_related('course', 'course__teacher')

    return render(request, 'courses/my_courses.html', {
        'enrollments': enrollments
    })


@login_required
def lesson_detail(request, pk):
    """Dars ko'rish"""
    lesson = get_object_or_404(Lesson, pk=pk)
    course = lesson.module.course

    # Yozilganligini tekshirish
    if request.user.is_student():
        enrollment = Enrollment.objects.filter(
            student=request.user,
            course=course,
            status='active'
        ).first()

        if not enrollment and not lesson.is_free:
            messages.error(request, 'Bu darsni ko\'rish uchun kursga yoziling!')
            return redirect('courses:detail', pk=course.pk)

    # Progress yaratish/yangilash
    progress = None
    if request.user.is_student():
        progress, _ = LessonProgress.objects.get_or_create(
            student=request.user,
            lesson=lesson
        )

    # Oldingi va keyingi darslar
    lessons = Lesson.objects.filter(module=lesson.module).order_by('order')
    lesson_list = list(lessons)
    current_index = lesson_list.index(lesson)

    prev_lesson = lesson_list[current_index - 1] if current_index > 0 else None
    next_lesson = lesson_list[current_index + 1] if current_index < len(lesson_list) - 1 else None

    return render(request, 'courses/lesson_detail.html', {
        'lesson': lesson,
        'course': course,
        'progress': progress,
        'prev_lesson': prev_lesson,
        'next_lesson': next_lesson
    })


@login_required
def lesson_complete(request, pk):
    """Darsni tugatish"""
    lesson = get_object_or_404(Lesson, pk=pk)

    if request.user.is_student():
        progress, _ = LessonProgress.objects.get_or_create(
            student=request.user,
            lesson=lesson
        )

        if not progress.is_completed:
            progress.is_completed = True
            progress.completed_at = timezone.now()
            progress.save()

            # Enrollment progressini yangilash
            enrollment = Enrollment.objects.filter(
                student=request.user,
                course=lesson.module.course
            ).first()

            if enrollment:
                enrollment.update_progress()

            messages.success(request, 'Dars tugatildi!')

    return redirect('courses:lesson_detail', pk=pk)


# ===================== O'QITUVCHI =====================

@login_required
def teacher_courses(request):
    """O'qituvchi kurslari"""
    if not request.user.is_teacher():
        messages.error(request, 'Sizda ruxsat yo\'q!')
        return redirect('accounts:dashboard')

    courses = Course.objects.filter(teacher=request.user)

    return render(request, 'courses/teacher/course_list.html', {
        'courses': courses
    })


@login_required
def teacher_course_create(request):
    """Yangi kurs yaratish"""
    if not request.user.is_teacher():
        messages.error(request, 'Sizda ruxsat yo\'q!')
        return redirect('accounts:dashboard')

    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():
            course = form.save(commit=False)
            course.teacher = request.user
            course.save()
            messages.success(request, 'Kurs yaratildi!')
            return redirect('courses:teacher_course_detail', pk=course.pk)
    else:
        form = CourseForm()

    return render(request, 'courses/teacher/course_form.html', {
        'form': form,
        'title': 'Yangi kurs'
    })


@login_required
def teacher_course_edit(request, pk):
    """Kursni tahrirlash"""
    course = get_object_or_404(Course, pk=pk, teacher=request.user)

    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, 'Kurs yangilandi!')
            return redirect('courses:teacher_course_detail', pk=pk)
    else:
        form = CourseForm(instance=course)

    return render(request, 'courses/teacher/course_form.html', {
        'form': form,
        'course': course,
        'title': 'Kursni tahrirlash'
    })


@login_required
def teacher_course_detail(request, pk):
    """O'qituvchi kurs tafsilotlari"""
    course = get_object_or_404(Course, pk=pk, teacher=request.user)
    modules = course.modules.prefetch_related('lessons').all()
    enrollments = course.enrollments.select_related('student').all()[:10]

    return render(request, 'courses/teacher/course_detail.html', {
        'course': course,
        'modules': modules,
        'enrollments': enrollments
    })


@login_required
def teacher_module_create(request, course_pk):
    """Modul yaratish"""
    course = get_object_or_404(Course, pk=course_pk, teacher=request.user)

    if request.method == 'POST':
        form = ModuleForm(request.POST)
        if form.is_valid():
            module = form.save(commit=False)
            module.course = course
            module.save()
            messages.success(request, 'Modul qo\'shildi!')
            return redirect('courses:teacher_course_detail', pk=course_pk)
    else:
        # Keyingi tartib raqamini olish
        last_order = course.modules.count()
        form = ModuleForm(initial={'order': last_order})

    return render(request, 'courses/teacher/module_form.html', {
        'form': form,
        'course': course,
        'title': 'Yangi modul'
    })


@login_required
def teacher_module_edit(request, pk):
    """Modulni tahrirlash"""
    module = get_object_or_404(Module, pk=pk, course__teacher=request.user)

    if request.method == 'POST':
        form = ModuleForm(request.POST, instance=module)
        if form.is_valid():
            form.save()
            messages.success(request, 'Modul yangilandi!')
            return redirect('courses:teacher_course_detail', pk=module.course.pk)
    else:
        form = ModuleForm(instance=module)

    return render(request, 'courses/teacher/module_form.html', {
        'form': form,
        'module': module,
        'course': module.course,
        'title': 'Modulni tahrirlash'
    })


@login_required
def teacher_module_delete(request, pk):
    """Modulni o'chirish"""
    module = get_object_or_404(Module, pk=pk, course__teacher=request.user)
    course_pk = module.course.pk

    if request.method == 'POST':
        module.delete()
        messages.success(request, 'Modul o\'chirildi!')
        return redirect('courses:teacher_course_detail', pk=course_pk)

    return render(request, 'courses/teacher/module_confirm_delete.html', {
        'module': module
    })


@login_required
def teacher_lesson_create(request, module_pk):
    """Dars yaratish"""
    module = get_object_or_404(Module, pk=module_pk, course__teacher=request.user)

    if request.method == 'POST':
        form = LessonForm(request.POST)
        if form.is_valid():
            lesson = form.save(commit=False)
            lesson.module = module
            lesson.save()
            messages.success(request, 'Dars qo\'shildi!')
            return redirect('courses:teacher_course_detail', pk=module.course.pk)
    else:
        last_order = module.lessons.count()
        form = LessonForm(initial={'order': last_order})

    return render(request, 'courses/teacher/lesson_form.html', {
        'form': form,
        'module': module,
        'course': module.course,
        'title': 'Yangi dars'
    })


@login_required
def teacher_lesson_edit(request, pk):
    """Darsni tahrirlash"""
    lesson = get_object_or_404(Lesson, pk=pk, module__course__teacher=request.user)

    if request.method == 'POST':
        form = LessonForm(request.POST, instance=lesson)
        if form.is_valid():
            form.save()
            messages.success(request, 'Dars yangilandi!')
            return redirect('courses:teacher_course_detail', pk=lesson.module.course.pk)
    else:
        form = LessonForm(instance=lesson)

    return render(request, 'courses/teacher/lesson_form.html', {
        'form': form,
        'lesson': lesson,
        'module': lesson.module,
        'course': lesson.module.course,
        'title': 'Darsni tahrirlash'
    })


@login_required
def teacher_lesson_delete(request, pk):
    """Darsni o'chirish"""
    lesson = get_object_or_404(Lesson, pk=pk, module__course__teacher=request.user)
    course_pk = lesson.module.course.pk

    if request.method == 'POST':
        lesson.delete()
        messages.success(request, 'Dars o\'chirildi!')
        return redirect('courses:teacher_course_detail', pk=course_pk)

    return render(request, 'courses/teacher/lesson_confirm_delete.html', {
        'lesson': lesson
    })