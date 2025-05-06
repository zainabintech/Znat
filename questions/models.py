from django.db import models
from django.contrib.auth.models import User
from quizzes.models import Quiz
from django.conf import settings
from courses.models import Course  # Import Course from the correct app

class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    text = models.TextField()
    correct_option_id = models.IntegerField()
    type = models.CharField(max_length=50)

    def __str__(self):
        return self.text

class Video(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='videos')
    title = models.CharField(max_length=255)
    video_file = models.FileField(upload_to='videos/')

    def __str__(self):
        return self.title

class PDF(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='pdfs')
    title = models.CharField(max_length=255)
    pdf_file = models.FileField(upload_to='pdfs/')

    def __str__(self):
        return self.title

class QuizQuestion(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='quiz_questions')
    question_text = models.TextField()
    option_a = models.CharField(max_length=255)
    option_b = models.CharField(max_length=255)
    option_c = models.CharField(max_length=255)
    option_d = models.CharField(max_length=255)
    correct_option = models.CharField(
        max_length=1,
        choices=[('A', 'Option A'), ('B', 'Option B'), ('C', 'Option C'), ('D', 'Option D')]
    )

    def __str__(self):
        return self.question_text

class EmployeeProgress(models.Model):
    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    quiz_score = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.employee.username} - {self.course.title}"

class MaterialProgress(models.Model):
    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    video = models.ForeignKey(Video, on_delete=models.CASCADE, null=True, blank=True)
    pdf = models.ForeignKey(PDF, on_delete=models.CASCADE, null=True, blank=True)
    completed = models.BooleanField(default=False)
    completed_date = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [['employee', 'video'], ['employee', 'pdf']]

    def __str__(self):
        material = self.video.title if self.video else self.pdf.title
        return f"{self.employee.username} - {material}"