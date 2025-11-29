# apps/attendance/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q

from .models import Session, Attendance
from .forms import SessionForm
from apps.courses.models import Course, Enrollment


# ===================== TALABA =====================

@login_required
def student_attendance(request):
    """Talaba davomati"""
    enrollments = Enrollment.objects.filter(
        student=request.user,
        status='active'
    ).select_related('course')

    attendance_data = []

    for enrollment in enrollments:
        sessions = Session.objects.filter(course=enrollment.course)
        total_sessions = sessions.count()

        if total_sessions > 0:
            attendances = Attendance.objects.filter(
                session__course=enrollment.course,
                student=request.user
            )

            present = attendances.filter(status='present').count()
            late = attendances.filter(status='late').count()
            absent = attendances.filter(status='absent').count()
            excused = attendances.filter(status='excused').count()

            percentage = int(((present + late + excused) / total_sessions) * 100) if total_sessions > 0 else 0
        else:
            present = late = absent = excused = 0
            percentage = 0

        attendance_data.append({
            'course': enrollment.course,
            'total_sessions': total_sessions,
            'present': present,
            'late': late,
            'absent': absent,
            'excused': excused,
            'percentage': percentage
        })

    return render(request, 'attendance/student_attendance.html', {
        'attendance_data': attendance_data
    })


@login_required
def student_attendance_detail(request, course_pk):
    """Talaba davomati tafsiloti"""
    course = get_object_or_404(Course, pk=course_pk)

    # Yozilganligini tekshirish
    enrollment = Enrollment.objects.filter(
        student=request.user,
        course=course
    ).first()

    if not enrollment:
        messages.error(request, 'Siz bu kursga yozilmagansiz!')
        return redirect('attendance:student_attendance')

    sessions = Session.objects.filter(course=course).order_by('-date')

    attendance_list = []
    for session in sessions:
        attendance = Attendance.objects.filter(
            session=session,
            student=request.user
        ).first()

        attendance_list.append({
            'session': session,
            'attendance': attendance
        })

    return render(request, 'attendance/student_attendance_detail.html', {
        'course': course,
        'attendance_list': attendance_list
    })


# ===================== O'QITUVCHI =====================

@login_required
def teacher_session_list(request):
    """O'qituvchi sessiyalari"""
    if not request.user.is_teacher():
        messages.error(request, 'Sizda ruxsat yo\'q!')
        return redirect('accounts:dashboard')

    sessions = Session.objects.filter(
        course__teacher=request.user
    ).select_related('course').order_by('-date')

    return render(request, 'attendance/teacher/session_list.html', {
        'sessions': sessions
    })


@login_required
def teacher_session_create(request, course_pk):
    """Sessiya yaratish"""
    course = get_object_or_404(Course, pk=course_pk, teacher=request.user)

    if request.method == 'POST':
        form = SessionForm(request.POST)
        if form.is_valid():
            session = form.save(commit=False)
            session.course = course
            session.save()
            messages.success(request, 'Sessiya yaratildi!')
            return redirect('attendance:teacher_take_attendance', pk=session.pk)
    else:
        form = SessionForm()

    return render(request, 'attendance/teacher/session_form.html', {
        'form': form,
        'course': course,
        'title': 'Yangi sessiya'
    })


@login_required
def teacher_session_edit(request, pk):
    """Sessiyani tahrirlash"""
    session = get_object_or_404(Session, pk=pk, course__teacher=request.user)

    if request.method == 'POST':
        form = SessionForm(request.POST, instance=session)
        if form.is_valid():
            form.save()
            messages.success(request, 'Sessiya yangilandi!')
            return redirect('attendance:teacher_session_list')
    else:
        form = SessionForm(instance=session)

    return render(request, 'attendance/teacher/session_form.html', {
        'form': form,
        'session': session,
        'course': session.course,
        'title': 'Sessiyani tahrirlash'
    })


@login_required
def teacher_session_delete(request, pk):
    """Sessiyani o'chirish"""
    session = get_object_or_404(Session, pk=pk, course__teacher=request.user)

    if request.method == 'POST':
        session.delete()
        messages.success(request, 'Sessiya o\'chirildi!')
        return redirect('attendance:teacher_session_list')

    return render(request, 'attendance/teacher/session_confirm_delete.html', {
        'session': session
    })


@login_required
def teacher_take_attendance(request, pk):
    """Davomat olish"""
    session = get_object_or_404(Session, pk=pk, course__teacher=request.user)

    # Kursga yozilgan talabalar
    enrollments = Enrollment.objects.filter(
        course=session.course,
        status='active'
    ).select_related('student')

    if request.method == 'POST':
        for enrollment in enrollments:
            student = enrollment.student
            status = request.POST.get(f'status_{student.pk}', 'absent')
            notes = request.POST.get(f'notes_{student.pk}', '')

            attendance, created = Attendance.objects.update_or_create(
                session=session,
                student=student,
                defaults={
                    'status': status,
                    'notes': notes
                }
            )

        messages.success(request, 'Davomat saqlandi!')
        return redirect('attendance:teacher_session_list')

    # Mavjud davomatlarni olish
    attendance_data = []
    for enrollment in enrollments:
        attendance = Attendance.objects.filter(
            session=session,
            student=enrollment.student
        ).first()

        attendance_data.append({
            'student': enrollment.student,
            'attendance': attendance
        })

    return render(request, 'attendance/teacher/take_attendance.html', {
        'session': session,
        'attendance_data': attendance_data
    })


@login_required
def teacher_attendance_report(request, course_pk):
    """Davomat hisoboti"""
    course = get_object_or_404(Course, pk=course_pk, teacher=request.user)

    sessions = Session.objects.filter(course=course).order_by('date')
    enrollments = Enrollment.objects.filter(
        course=course,
        status='active'
    ).select_related('student')

    # Har bir talaba uchun davomat
    report_data = []
    for enrollment in enrollments:
        student_attendances = []
        present_count = 0

        for session in sessions:
            attendance = Attendance.objects.filter(
                session=session,
                student=enrollment.student
            ).first()

            student_attendances.append(attendance)

            if attendance and attendance.status in ['present', 'late', 'excused']:
                present_count += 1

        total = sessions.count()
        percentage = int((present_count / total) * 100) if total > 0 else 0

        report_data.append({
            'student': enrollment.student,
            'attendances': student_attendances,
            'present_count': present_count,
            'total': total,
            'percentage': percentage
        })

    return render(request, 'attendance/teacher/attendance_report.html', {
        'course': course,
        'sessions': sessions,
        'report_data': report_data
    })