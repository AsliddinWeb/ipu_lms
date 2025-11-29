# apps/content/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import FileResponse, Http404

from .models import Material
from .forms import MaterialForm
from apps.courses.models import Course, Enrollment


# ===================== TALABA =====================

@login_required
def material_list(request, course_pk):
    """Kurs materiallari"""
    course = get_object_or_404(Course, pk=course_pk)

    # Yozilganligini tekshirish
    enrollment = Enrollment.objects.filter(
        student=request.user,
        course=course,
        status='active'
    ).first()

    # O'qituvchi yoki yozilgan talaba ko'ra oladi
    if not enrollment and course.teacher != request.user:
        messages.error(request, 'Bu materiallarga kirish uchun kursga yoziling!')
        return redirect('courses:detail', pk=course_pk)

    materials = Material.objects.filter(
        course=course,
        is_active=True
    ).select_related('lesson')

    return render(request, 'content/material_list.html', {
        'course': course,
        'materials': materials
    })


@login_required
def material_download(request, pk):
    """Materialni yuklab olish"""
    material = get_object_or_404(Material, pk=pk, is_active=True)

    # Yozilganligini tekshirish
    enrollment = Enrollment.objects.filter(
        student=request.user,
        course=material.course,
        status='active'
    ).first()

    if not enrollment and material.course.teacher != request.user:
        messages.error(request, 'Bu materialni yuklab olish uchun kursga yoziling!')
        return redirect('courses:detail', pk=material.course.pk)

    if material.material_type == 'link':
        return redirect(material.url)

    if not material.file:
        raise Http404("Fayl topilmadi")

    # Yuklab olishlar sonini oshirish
    material.download_count += 1
    material.save(update_fields=['download_count'])

    return FileResponse(
        material.file.open('rb'),
        as_attachment=True,
        filename=material.file.name.split('/')[-1]
    )


# ===================== O'QITUVCHI =====================

@login_required
def teacher_material_list(request, course_pk):
    """O'qituvchi materiallari"""
    if not request.user.is_teacher():
        messages.error(request, 'Sizda ruxsat yo\'q!')
        return redirect('accounts:dashboard')

    course = get_object_or_404(Course, pk=course_pk, teacher=request.user)

    materials = Material.objects.filter(
        course=course
    ).select_related('lesson')

    return render(request, 'content/teacher/material_list.html', {
        'course': course,
        'materials': materials
    })


@login_required
def teacher_material_create(request, course_pk):
    """Material qo'shish"""
    course = get_object_or_404(Course, pk=course_pk, teacher=request.user)

    if request.method == 'POST':
        form = MaterialForm(request.POST, request.FILES, course=course)
        if form.is_valid():
            material = form.save(commit=False)
            material.course = course
            material.save()
            messages.success(request, 'Material qo\'shildi!')
            return redirect('content:teacher_material_list', course_pk=course_pk)
    else:
        form = MaterialForm(course=course)

    return render(request, 'content/teacher/material_form.html', {
        'form': form,
        'course': course,
        'title': 'Yangi material'
    })


@login_required
def teacher_material_edit(request, pk):
    """Materialni tahrirlash"""
    material = get_object_or_404(Material, pk=pk, course__teacher=request.user)
    course = material.course

    if request.method == 'POST':
        form = MaterialForm(request.POST, request.FILES, instance=material, course=course)
        if form.is_valid():
            form.save()
            messages.success(request, 'Material yangilandi!')
            return redirect('content:teacher_material_list', course_pk=course.pk)
    else:
        form = MaterialForm(instance=material, course=course)

    return render(request, 'content/teacher/material_form.html', {
        'form': form,
        'material': material,
        'course': course,
        'title': 'Materialni tahrirlash'
    })


@login_required
def teacher_material_delete(request, pk):
    """Materialni o'chirish"""
    material = get_object_or_404(Material, pk=pk, course__teacher=request.user)

    if request.method == 'POST':
        course_pk = material.course.pk
        material.delete()
        messages.success(request, 'Material o\'chirildi!')
        return redirect('content:teacher_material_list', course_pk=course_pk)

    return render(request, 'content/teacher/material_confirm_delete.html', {
        'material': material
    })