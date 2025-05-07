from django.db import models
from users.models import CustomUser
from django.utils import timezone

class Course(models.Model):
    LEVEL_CHOICES = [
        (1, 'Level 1 - Basic'),
        (2, 'Level 2 - Intermediate'),
        (3, 'Level 3 - Advanced')
    ]
    
    title = models.CharField(max_length=200)
    desc = models.TextField()
    level = models.IntegerField(choices=LEVEL_CHOICES)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    prerequisites = models.ManyToManyField('self', blank=True, symmetrical=False)
    min_pass_score = models.FloatField(default=70.0)

    class Meta:
        ordering = ['level', 'title']

    def __str__(self):
        return self.title

    def get_progress(self, user):
        from questions.models import MaterialProgress, EmployeeProgress
        
        # Get material completion stats
        total_materials = self.videos.count() + self.pdfs.count()
        completed_materials = MaterialProgress.objects.filter(
            employee=user,
            course=self,
            completed=True
        ).count()
        
        progress = (completed_materials / total_materials * 100) if total_materials > 0 else 0
        
        # Get quiz progress
        quiz_progress = EmployeeProgress.objects.filter(
            employee=user,
            course=self
        ).first()
        
        return {
            'total_materials': total_materials,
            'completed_materials': completed_materials,
            'progress': progress,
            'quiz_completed': quiz_progress.completed if quiz_progress else False,
            'quiz_score': quiz_progress.quiz_score if quiz_progress else 0,
        }

    def is_available_for_user(self, user):
        if user.is_admin():
            return True
            
        # Check if user is at the right level
        if user.current_level != self.level:
            return False
            
        # For level 1, always available
        if self.level == 1:
            return True
            
        # Check prerequisites
        for prereq in self.prerequisites.all():
            progress = EmployeeProgress.objects.filter(
                employee=user,
                course=prereq,
                completed=True
            ).exists()
            if not progress:
                return False
                
        return True