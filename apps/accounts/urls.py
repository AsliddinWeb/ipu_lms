# apps/accounts/urls.py

from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Auth
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Register
    path('register/student/', views.register_student, name='register_student'),
    # path('register/teacher/', views.register_teacher, name='register_teacher'),

    # Profile & Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
]