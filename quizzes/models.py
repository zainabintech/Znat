from django.db import models

# Create your models here.
from django.db import models

# Create your models here.
from django.db import models
from users.models import CustomUser
from courses.models import Course

class Quiz(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    passing_score = models.FloatField(default=70.0)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    def __str__(self):
        return f"Quiz for {self.course.title}"