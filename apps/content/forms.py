# apps/content/forms.py

from django import forms
from .models import Material
from apps.courses.models import Lesson


class MaterialForm(forms.ModelForm):
    """Material formasi"""

    class Meta:
        model = Material
        fields = ('title', 'description', 'material_type', 'lesson', 'file', 'url', 'is_active')
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Material nomi'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Tavsif (ixtiyoriy)'
            }),
            'material_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'lesson': forms.Select(attrs={
                'class': 'form-select'
            }),
            'file': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://...'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }

    def __init__(self, *args, **kwargs):
        course = kwargs.pop('course', None)
        super().__init__(*args, **kwargs)

        if course:
            self.fields['lesson'].queryset = Lesson.objects.filter(
                module__course=course
            ).select_related('module')
            self.fields['lesson'].required = False

        self.fields['lesson'].empty_label = "Umumiy (darsga bog'lanmagan)"

    def clean(self):
        cleaned_data = super().clean()
        material_type = cleaned_data.get('material_type')
        file = cleaned_data.get('file')
        url = cleaned_data.get('url')

        if material_type == 'link':
            if not url:
                raise forms.ValidationError('Havola turi uchun URL kiritish majburiy!')
        else:
            if not file and not self.instance.pk:
                raise forms.ValidationError('Fayl yuklash majburiy!')

        return cleaned_data