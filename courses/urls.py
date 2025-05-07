from django.urls import path
from . import views

urlpatterns = [
    path('', views.course_list, name='course_list'),
    path('wizard/<int:step>/', views.course_wizard, name='course_wizard'),
    path('wizard/<int:step>/<int:course_id>/', views.course_wizard, name='course_wizard'),
    path('create/', views.course_create, name='course_create'),
    path('<int:pk>/', views.course_detail, name='course_detail'),
    path('<int:pk>/update/', views.course_update, name='course_update'),
    path('<int:pk>/delete/', views.course_delete, name='course_delete'),
]