from django.urls import path
from . import views
from questions import views as question_views

urlpatterns = [
    path('', views.quiz_list, name='quiz_list'),
    path('create/<int:course_id>/', views.quiz_create, name='quiz_create'),
    path('<int:pk>/', views.quiz_detail, name='quiz_detail'),
    path('<int:pk>/take/', views.quiz_take, name='quiz_take'),
    path('<int:pk>/result/', views.quiz_result, name='quiz_result'),
    path('<int:quiz_id>/questions/create/', question_views.question_create, name='question_create'),
]