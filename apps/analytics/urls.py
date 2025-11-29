# apps/analytics/urls.py

from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    # Talaba
    path('', views.student_stats, name='student_stats'),

    # O'qituvchi
    path('teacher/course/<int:course_pk>/', views.teacher_course_analytics, name='teacher_course_analytics'),
    path('teacher/course/<int:course_pk>/student/<int:student_pk>/', views.teacher_student_progress,
         name='teacher_student_progress'),
]