from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('Admin', 'Admin'),
        ('Employee', 'Employee')
    ]
    
    # Override AbstractUser fields
    first_name = None
    last_name = None
    
    # Custom fields
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
        return self.is_superuser or self.role == 'Admin'

    def is_employee(self):
        return not self.is_superuser and self.role == 'Employee'

    def save(self, *args, **kwargs):
        # Ensure superusers and admin users start at max level
        if self.is_superuser or self.role == 'Admin':
            self.current_level = 3
            self.role = 'Admin'  # Ensure superusers are always admins
        super().save(*args, **kwargs)