# apps/attendance/forms.py

from django import forms
from .models import Session, Attendance


class SessionForm(forms.ModelForm):
    """Sessiya formasi"""
    class Meta:
        model = Session
        fields = ('title', 'session_type', 'date', 'start_time', 'end_time')
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Dars mavzusi'
            }),
            'session_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'start_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'end_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
        }


class AttendanceForm(forms.ModelForm):
    """Davomat formasi"""
    class Meta:
        model = Attendance
        fields = ('status', 'notes')
        widgets = {
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'notes': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Izoh (ixtiyoriy)'
            }),
        }