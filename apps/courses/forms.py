# apps/courses/forms.py

from django import forms
from .models import Course, Module, Lesson, Enrollment


class CourseForm(forms.ModelForm):
    """Kurs formasi"""
    class Meta:
        model = Course
        fields = ('name', 'code', 'description', 'image', 'department', 'credits', 'is_active')
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Kurs nomi'
            }),
            'code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Masalan: INF101'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Kurs haqida qisqacha...'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'department': forms.Select(attrs={
                'class': 'form-select'
            }),
            'credits': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 10
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }


class ModuleForm(forms.ModelForm):
    """Modul formasi"""
    class Meta:
        model = Module
        fields = ('title', 'description', 'order')
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Modul nomi'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Modul haqida...'
            }),
            'order': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0
            }),
        }


class LessonForm(forms.ModelForm):
    """Dars formasi"""
    class Meta:
        model = Lesson
        fields = ('title', 'content', 'video_url', 'duration_minutes', 'order', 'is_free')
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Dars nomi'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Dars matni...'
            }),
            'video_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://youtube.com/...'
            }),
            'duration_minutes': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'placeholder': 'Daqiqada'
            }),
            'order': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0
            }),
            'is_free': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }


class EnrollmentForm(forms.ModelForm):
    """Kursga yozilish formasi"""
    class Meta:
        model = Enrollment
        fields = ('course',)
        widgets = {
            'course': forms.HiddenInput()
        }