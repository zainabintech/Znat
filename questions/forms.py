from django import forms
from .models import Video, PDF, QuizQuestion, Question
from django.core.exceptions import ValidationError

class VideoForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = ['title', 'course', 'video_file']

    def clean_video_file(self):
        file = self.cleaned_data.get('video_file')
        if file:
            if not file.content_type.startswith('video/'):
                raise ValidationError('Invalid video format')
            if file.size > 104857600:  # 100MB
                raise ValidationError('Video file too large (max 100MB)')
        return file

class PDFForm(forms.ModelForm):
    class Meta:
        model = PDF
        fields = ['title', 'course', 'pdf_file']

    def clean_pdf_file(self):
        file = self.cleaned_data.get('pdf_file')
        if file:
            if file.content_type != 'application/pdf':
                raise ValidationError('File must be a PDF')
            if file.size > 10485760:  # 10MB
                raise ValidationError('PDF file too large (max 10MB)')
        return file

class QuizQuestionForm(forms.ModelForm):
    class Meta:
        model = QuizQuestion
        fields = ['course', 'question_text', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_option']
        widgets = {
            'question_text': forms.Textarea(attrs={'rows': 3}),
            'option_a': forms.TextInput(attrs={'class': 'form-control'}),
            'option_b': forms.TextInput(attrs={'class': 'form-control'}),
            'option_c': forms.TextInput(attrs={'class': 'form-control'}),
            'option_d': forms.TextInput(attrs={'class': 'form-control'}),
            'correct_option': forms.Select(attrs={'class': 'form-select'})
        }

    def clean(self):
        cleaned_data = super().clean()
        if not any([cleaned_data.get(f'option_{opt}') for opt in ['a', 'b', 'c', 'd']]):
            raise ValidationError('At least one option must be provided')
        return cleaned_data

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['quiz', 'text', 'correct_option_id', 'type']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3}),
            'type': forms.Select(choices=[
                ('multiple_choice', 'Multiple Choice'),
                ('true_false', 'True/False')
            ])
        }

    def clean_correct_option_id(self):
        option_id = self.cleaned_data.get('correct_option_id')
        qtype = self.cleaned_data.get('type')
        if qtype == 'true_false' and option_id not in [0, 1]:
            raise ValidationError('For True/False questions, correct option must be 0 (False) or 1 (True)')
        elif qtype == 'multiple_choice' and not (0 <= option_id <= 3):
            raise ValidationError('For multiple choice questions, correct option must be between 0 and 3')
        return option_id
