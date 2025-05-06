from django import forms
from .models import Video, PDF, QuizQuestion, Question
from django.core.exceptions import ValidationError

class VideoForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = ['title', 'course', 'video_file']

    def clean_video_file(self):
        video = self.cleaned_data.get('video_file')
        if video:
            if video.size > 104857600:  # 100MB
                raise ValidationError('Video file too large (max 100MB)')
        return video

class PDFForm(forms.ModelForm):
    class Meta:
        model = PDF
        fields = ['title', 'course', 'pdf_file']

    def clean_pdf_file(self):
        pdf = self.cleaned_data.get('pdf_file')
        if pdf:
            if pdf.size > 10485760:  # 10MB
                raise ValidationError('PDF file too large (max 10MB)')
        return pdf

class QuizQuestionForm(forms.ModelForm):
    class Meta:
        model = QuizQuestion
        fields = ['course', 'question_text', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_option']
        widgets = {
            'question_text': forms.Textarea(attrs={'rows': 3}),
            'correct_option': forms.RadioSelect(choices=[
                ('A', 'Option A'),
                ('B', 'Option B'),
                ('C', 'Option C'),
                ('D', 'Option D')
            ])
        }

    def clean(self):
        cleaned_data = super().clean()
        # Ensure all options are unique
        options = [
            cleaned_data.get('option_a'),
            cleaned_data.get('option_b'),
            cleaned_data.get('option_c'),
            cleaned_data.get('option_d')
        ]
        if len(set(filter(None, options))) != len(list(filter(None, options))):
            raise ValidationError('All options must be unique')
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
        question_type = self.cleaned_data.get('type')
        
        if question_type == 'true_false' and option_id not in [0, 1]:
            raise ValidationError('For True/False questions, correct option must be 0 (False) or 1 (True)')
        elif question_type == 'multiple_choice' and not (0 <= option_id <= 3):
            raise ValidationError('For Multiple Choice questions, correct option must be between 0 and 3')
            
        return option_id
