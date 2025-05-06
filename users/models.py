from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('Admin', 'Admin'),
        ('Employee', 'Employee')
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    current_level = models.IntegerField(default=1)
    latest_score = models.FloatField(null=True, blank=True)

    class Meta:
        permissions = [
            ("can_view_admin_dashboard", "Can view admin dashboard"),
            ("can_manage_courses", "Can manage courses"),
            ("can_take_quizzes", "Can take quizzes"),
        ]

    def __str__(self):
        return self.username

    def is_admin(self):
        return self.role == 'Admin'

    def is_employee(self):
        return self.role == 'Employee'

    def save(self, *args, **kwargs):
        # Ensure admin users start at max level
        if self.role == 'Admin' and self.current_level < 3:
            self.current_level = 3
        super().save(*args, **kwargs)