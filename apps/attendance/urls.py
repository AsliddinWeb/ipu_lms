# apps/attendance/urls.py

from django.urls import path
from . import views

app_name = 'attendance'

urlpatterns = [
    # Talaba
    path('', views.student_attendance, name='student_attendance'),
    path('course/<int:course_pk>/', views.student_attendance_detail, name='student_attendance_detail'),

    # O'qituvchi
    path('teacher/', views.teacher_session_list, name='teacher_session_list'),
    path('teacher/course/<int:course_pk>/create/', views.teacher_session_create, name='teacher_session_create'),
    path('teacher/session/<int:pk>/edit/', views.teacher_session_edit, name='teacher_session_edit'),
    path('teacher/session/<int:pk>/delete/', views.teacher_session_delete, name='teacher_session_delete'),
    path('teacher/session/<int:pk>/take/', views.teacher_take_attendance, name='teacher_take_attendance'),
    path('teacher/course/<int:course_pk>/report/', views.teacher_attendance_report, name='teacher_attendance_report'),
]