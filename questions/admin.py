from django.contrib import admin
from .models import Question, Video, PDF, QuizQuestion, EmployeeProgress

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('quiz', 'text', 'type', 'correct_option_id')
    list_filter = ('quiz', 'type')
    search_fields = ('text', 'quiz__course__title')

@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ('title', 'course')
    list_filter = ('course',)
    search_fields = ('title', 'course__title')

@admin.register(PDF)
class PDFAdmin(admin.ModelAdmin):
    list_display = ('title', 'course')
    list_filter = ('course',)
    search_fields = ('title', 'course__title')

@admin.register(QuizQuestion)
class QuizQuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'course', 'correct_option')
    list_filter = ('course', 'correct_option')
    search_fields = ('question_text', 'course__title')

@admin.register(EmployeeProgress)
class EmployeeProgressAdmin(admin.ModelAdmin):
    list_display = ('employee', 'course', 'completed', 'quiz_score')
    list_filter = ('completed', 'course__level')
    search_fields = ('employee__username', 'course__title')
