# apps/courses/urls.py

from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    # Umumiy
    path('', views.course_list, name='list'),
    path('<int:pk>/', views.course_detail, name='detail'),
    path('<int:pk>/enroll/', views.course_enroll, name='enroll'),
    path('<int:pk>/unenroll/', views.course_unenroll, name='unenroll'),

    # Talaba
    path('my/', views.my_courses, name='my_courses'),
    path('lesson/<int:pk>/', views.lesson_detail, name='lesson_detail'),
    path('lesson/<int:pk>/complete/', views.lesson_complete, name='lesson_complete'),

    # O'qituvchi
    path('teacher/', views.teacher_courses, name='teacher_courses'),
    path('teacher/create/', views.teacher_course_create, name='teacher_course_create'),
    path('teacher/<int:pk>/', views.teacher_course_detail, name='teacher_course_detail'),
    path('teacher/<int:pk>/edit/', views.teacher_course_edit, name='teacher_course_edit'),

    # O'qituvchi - Modul
    path('teacher/<int:course_pk>/module/create/', views.teacher_module_create, name='teacher_module_create'),
    path('teacher/module/<int:pk>/edit/', views.teacher_module_edit, name='teacher_module_edit'),
    path('teacher/module/<int:pk>/delete/', views.teacher_module_delete, name='teacher_module_delete'),

    # O'qituvchi - Dars
    path('teacher/module/<int:module_pk>/lesson/create/', views.teacher_lesson_create, name='teacher_lesson_create'),
    path('teacher/lesson/<int:pk>/edit/', views.teacher_lesson_edit, name='teacher_lesson_edit'),
    path('teacher/lesson/<int:pk>/delete/', views.teacher_lesson_delete, name='teacher_lesson_delete'),
]