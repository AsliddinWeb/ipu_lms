# apps/main/urls.py

from django.urls import path
from . import views

app_name = 'main'

urlpatterns = [
    path('', views.landing_page, name='landing'),
    path('about/', views.about_page, name='about'),
    path('contact/', views.contact_page, name='contact'),
]