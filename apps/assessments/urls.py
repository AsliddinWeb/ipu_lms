# apps/assessments/urls.py

from django.urls import path
from . import views

app_name = 'assessments'

urlpatterns = [
    # Talaba
    path('', views.quiz_list, name='quiz_list'),
    path('<int:pk>/', views.quiz_detail, name='quiz_detail'),
    path('<int:pk>/start/', views.quiz_start, name='quiz_start'),
    path('take/<int:pk>/', views.quiz_take, name='quiz_take'),
    path('result/<int:pk>/', views.quiz_result, name='quiz_result'),
    path('gradebook/', views.gradebook, name='gradebook'),

    # O'qituvchi
    path('teacher/', views.teacher_quiz_list, name='teacher_quiz_list'),
    path('teacher/course/<int:course_pk>/create/', views.teacher_quiz_create, name='teacher_quiz_create'),
    path('teacher/<int:pk>/', views.teacher_quiz_detail, name='teacher_quiz_detail'),
    path('teacher/<int:pk>/edit/', views.teacher_quiz_edit, name='teacher_quiz_edit'),
    path('teacher/<int:pk>/delete/', views.teacher_quiz_delete, name='teacher_quiz_delete'),
    path('teacher/<int:pk>/results/', views.teacher_quiz_results, name='teacher_quiz_results'),

    # O'qituvchi - Savol
    path('teacher/quiz/<int:quiz_pk>/question/create/', views.teacher_question_create, name='teacher_question_create'),
    path('teacher/question/<int:pk>/edit/', views.teacher_question_edit, name='teacher_question_edit'),
    path('teacher/question/<int:pk>/delete/', views.teacher_question_delete, name='teacher_question_delete'),
]