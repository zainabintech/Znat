from django.contrib import admin
from .models import Quiz

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('course', 'passing_score', 'user')
    list_filter = ('course__level', 'passing_score')
    search_fields = ('course__title',)
