from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Count, Q
from django.db import transaction
from django.utils import timezone
from .models import Course
from users.models import CustomUser
from django import forms
from questions.models import Video, PDF, MaterialProgress, EmployeeProgress, Question
from quizzes.models import Quiz

def is_employee(user):
    return user.is_authenticated and user.role == 'Employee'

def is_admin(user):
    return user.is_authenticated and user.role == 'Admin'

@login_required
def course_list(request):
    if request.user.is_admin():
        courses = Course.objects.all()
    else:
        courses = Course.objects.filter(level=request.user.current_level)
    
    for course in courses:
        if request.user.is_employee():
            progress = EmployeeProgress.objects.filter(
                employee=request.user,
                course=course
            ).first()
            course.completed = progress and progress.completed
            course.progress_percentage = calculate_course_progress(request.user, course)
    
    return render(request, 'course_list.html', {'courses': courses})

@login_required
def course_detail(request, pk):
    course = get_object_or_404(Course, pk=pk)
    
    # Check access level for employees
    if not request.user.is_admin() and course.level != request.user.current_level:
        messages.error(request, 'Access denied. This course is not for your current level.')
        return redirect('course_list')
    
    # Handle material completion marking for employees
    if request.method == 'POST' and request.user.is_employee():
        try:
            with transaction.atomic():
                material_type = request.POST.get('material_type')
                material_id = request.POST.get('material_id')
                action = request.POST.get('action', 'complete')
                
                if material_type and material_id:
                    if material_type == 'video':
                        video = get_object_or_404(Video, id=material_id, course=course)
                        progress, created = MaterialProgress.objects.get_or_create(
                            employee=request.user,
                            course=course,
                            video=video
                        )
                    elif material_type == 'pdf':
                        pdf = get_object_or_404(PDF, id=material_id, course=course)
                        progress, created = MaterialProgress.objects.get_or_create(
                            employee=request.user,
                            course=course,
                            pdf=pdf
                        )
                    
                    progress.completed = (action == 'complete')
                    progress.save()
                    
                    # Check if all materials are completed
                    update_course_completion(request.user, course)
                    
                    messages.success(request, f'Progress updated successfully')
        except Exception as e:
            messages.error(request, f'Error updating progress: {str(e)}')
    
    # Get course materials and progress
    videos = Video.objects.filter(course=course)
    pdfs = PDF.objects.filter(course=course)
    
    if request.user.is_employee():
        # Get progress for each material
        for video in videos:
            video.completed = MaterialProgress.objects.filter(
                employee=request.user,
                video=video,
                completed=True
            ).exists()
        
        for pdf in pdfs:
            pdf.completed = MaterialProgress.objects.filter(
                employee=request.user,
                pdf=pdf,
                completed=True
            ).exists()
        
        course_progress = calculate_course_progress(request.user, course)
        quiz_available = is_quiz_available(request.user, course)
    else:
        course_progress = None
        quiz_available = True
    
    context = {
        'course': course,
        'videos': videos,
        'pdfs': pdfs,
        'progress': course_progress,
        'quiz_available': quiz_available,
        'is_admin': request.user.is_admin()
    }
    
    return render(request, 'course_detail.html', context)

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'desc', 'level']
        labels = {
            'desc': 'Description',
        }
        widgets = {
            'desc': forms.Textarea(attrs={'rows': 4}),
        }

@login_required
@user_passes_test(is_admin)
def course_create(request):
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    course = form.save(commit=False)
                    course.user = request.user
                    course.created_at = timezone.now()
                    course.updated_at = timezone.now()
                    course.save()
                    messages.success(request, 'Course created successfully')
                    return redirect('course_list')
            except Exception as e:
                messages.error(request, f'Error creating course: {str(e)}')
    else:
        form = CourseForm()
    return render(request, 'course_form.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def course_update(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            try:
                with transaction.atomic():
                    course = form.save(commit=False)
                    course.updated_at = timezone.now()
                    course.save()
                    messages.success(request, 'Course updated successfully')
                    return redirect('course_list')
            except Exception as e:
                messages.error(request, f'Error updating course: {str(e)}')
    else:
        form = CourseForm(instance=course)
    return render(request, 'course_form.html', {'form': form, 'course': course})

@login_required
@user_passes_test(is_admin)
def course_delete(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.method == 'POST':
        try:
            course.delete()
            messages.success(request, 'Course deleted successfully')
        except Exception as e:
            messages.error(request, f'Error deleting course: {str(e)}')
        return redirect('course_list')
    return render(request, 'course_confirm_delete.html', {'course': course})

@login_required
@user_passes_test(is_admin)
def course_wizard(request, step, course_id=None):
    # Calculate progress percentage
    progress = (step / 4) * 100
    
    if step == 1:
        if request.method == 'POST':
            form = CourseForm(request.POST)
            if form.is_valid():
                course = form.save(commit=False)
                course.user = request.user
                course.created_at = timezone.now()
                course.updated_at = timezone.now()
                course.save()
                return redirect('course_wizard', step=2, course_id=course.id)
        else:
            form = CourseForm()
        return render(request, 'course_wizard.html', {
            'step': step,
            'progress': progress,
            'form': form
        })
    
    # For steps 2-4, we need an existing course
    course = get_object_or_404(Course, pk=course_id)
    
    if step == 2:
        # Pass the course_id in the context so the template can add it to the form
        return render(request, 'course_wizard.html', {
            'step': step,
            'progress': progress,
            'course': course,
            'upload_url': f'/questions/upload-materials/?course_id={course_id}'
        })
    
    elif step == 3:
        if request.method == 'POST':
            # Create quiz
            quiz = Quiz.objects.create(
                course=course,
                passing_score=float(request.POST.get('passing_score', 70)),
                user=request.user
            )
            return redirect('course_wizard', step=4, course_id=course.id)
        return render(request, 'course_wizard.html', {
            'step': step,
            'progress': progress,
            'course': course
        })
    
    elif step == 4:
        if request.method == 'POST':
            # Create question
            question = Question.objects.create(
                quiz=course.quiz_set.first(),
                text=request.POST['text'],
                type=request.POST['type'],
                correct_option_id=request.POST['correct_option_id']
            )
            if 'add_another' in request.POST:
                return redirect('course_wizard', step=4, course_id=course.id)
            return redirect('course_detail', pk=course.id)
        return render(request, 'course_wizard.html', {
            'step': step,
            'progress': progress,
            'course': course,
            'quiz': course.quiz_set.first()
        })

    return redirect('course_list')

def calculate_course_progress(user, course):
    if not user.is_employee():
        return None
        
    total_materials = Video.objects.filter(course=course).count() + PDF.objects.filter(course=course).count()
    if total_materials == 0:
        return 0
        
    completed_materials = MaterialProgress.objects.filter(
        employee=user,
        course=course,
        completed=True
    ).count()
    
    return (completed_materials / total_materials) * 100

def is_quiz_available(user, course):
    if user.is_admin():
        return True
        
    total_materials = Video.objects.filter(course=course).count() + PDF.objects.filter(course=course).count()
    completed_materials = MaterialProgress.objects.filter(
        employee=user,
        course=course,
        completed=True
    ).count()
    
    return completed_materials == total_materials

def update_course_completion(user, course):
    total_materials = Video.objects.filter(course=course).count() + PDF.objects.filter(course=course).count()
    completed_materials = MaterialProgress.objects.filter(
        employee=user,
        course=course,
        completed=True
    ).count()
    
    progress, created = EmployeeProgress.objects.get_or_create(
        employee=user,
        course=course
    )
    
    # Mark as completed only if all materials are done and quiz is passed
    progress.completed = (
        completed_materials == total_materials and
        progress.quiz_score >= Quiz.objects.filter(course=course).first().passing_score
    )
    progress.save()