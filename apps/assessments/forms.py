# apps/assessments/forms.py

from django import forms
from .models import Quiz, Question, Answer


class QuizForm(forms.ModelForm):
    """Test formasi"""

    class Meta:
        model = Quiz
        fields = (
            'title', 'description', 'time_limit_minutes',
            'passing_score', 'attempts_allowed', 'shuffle_questions',
            'show_correct_answers', 'available_from', 'available_until', 'is_active'
        )
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Test nomi'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Test haqida...'
            }),
            'time_limit_minutes': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'placeholder': 'Masalan: 30'
            }),
            'passing_score': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'max': 100
            }),
            'attempts_allowed': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1
            }),
            'shuffle_questions': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'show_correct_answers': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'available_from': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'available_until': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }


class QuestionForm(forms.ModelForm):
    """Savol formasi"""

    class Meta:
        model = Question
        fields = ('question_type', 'text', 'points', 'order')
        widgets = {
            'question_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Savol matnini kiriting...'
            }),
            'points': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1
            }),
            'order': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0
            }),
        }


class AnswerForm(forms.ModelForm):
    """Javob formasi"""

    class Meta:
        model = Answer
        fields = ('text', 'is_correct', 'order')
        widgets = {
            'text': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Javob matni'
            }),
            'is_correct': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'order': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0
            }),
        }


# Javoblar uchun formset
AnswerFormSet = forms.inlineformset_factory(
    Question,
    Answer,
    form=AnswerForm,
    extra=4,
    can_delete=True,
    min_num=2,
    validate_min=True
)


class QuizTakeForm(forms.Form):
    """Test topshirish formasi - dinamik yaratiladi"""

    def __init__(self, quiz, *args, **kwargs):
        super().__init__(*args, **kwargs)

        questions = quiz.questions.prefetch_related('answers').all()

        for question in questions:
            field_name = f'question_{question.pk}'
            answers = question.answers.all()
            choices = [(a.pk, a.text) for a in answers]

            if question.question_type == Question.Type.SINGLE:
                self.fields[field_name] = forms.ChoiceField(
                    label=question.text,
                    choices=choices,
                    widget=forms.RadioSelect(attrs={
                        'class': 'form-check-input'
                    }),
                    required=True
                )
            elif question.question_type == Question.Type.MULTIPLE:
                self.fields[field_name] = forms.MultipleChoiceField(
                    label=question.text,
                    choices=choices,
                    widget=forms.CheckboxSelectMultiple(attrs={
                        'class': 'form-check-input'
                    }),
                    required=True
                )
            elif question.question_type == Question.Type.TRUE_FALSE:
                self.fields[field_name] = forms.ChoiceField(
                    label=question.text,
                    choices=choices,
                    widget=forms.RadioSelect(attrs={
                        'class': 'form-check-input'
                    }),
                    required=True
                )