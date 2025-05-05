from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    role = models.CharField(max_length=10, choices=[('Admin', 'Admin'), ('Employee', 'Employee')])
    current_level = models.IntegerField(default=1)
    latest_score = models.FloatField(null=True, blank=True)

    def __str__(self):
        return self.username