from django.urls import path
from . import views

urlpatterns = [
    path('materials/upload/', views.upload_course_material, name='upload_course_material'),
    path('quiz/<int:quiz_id>/questions/create/', views.create_quiz_question, name='create_quiz_question'),
    path('quiz/<int:quiz_id>/questions/', views.quiz_questions_list, name='quiz_questions_list'),
    path('quiz/<int:quiz_id>/questions/<int:question_id>/', views.quiz_question_detail, name='quiz_question_detail'),
]