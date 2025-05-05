from django.db import models

# Create your models here.
from django.db import models
from users.models import CustomUser

class Course(models.Model):
    title = models.CharField(max_length=200)
    desc = models.TextField()
    level = models.IntegerField(choices=[(1, 'Level 1'), (2, 'Level 2'), (3, 'Level 3')])
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    def __str__(self):
        return self.title