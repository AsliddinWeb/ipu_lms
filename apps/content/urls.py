# apps/content/urls.py

from django.urls import path
from . import views

app_name = 'content'

urlpatterns = [
    # Talaba
    path('course/<int:course_pk>/', views.material_list, name='material_list'),
    path('download/<int:pk>/', views.material_download, name='material_download'),

    # O'qituvchi
    path('teacher/course/<int:course_pk>/', views.teacher_material_list, name='teacher_material_list'),
    path('teacher/course/<int:course_pk>/create/', views.teacher_material_create, name='teacher_material_create'),
    path('teacher/<int:pk>/edit/', views.teacher_material_edit, name='teacher_material_edit'),
    path('teacher/<int:pk>/delete/', views.teacher_material_delete, name='teacher_material_delete'),
]