from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),
    path('courses/', include('courses.urls')),
    path('quizzes/', include('quizzes.urls')),
    path('questions/', include('questions.urls')),
    path('', TemplateView.as_view(template_name='landing.html'), name='landing'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

