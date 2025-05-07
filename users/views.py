from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Avg, Count
from .models import CustomUser
from courses.models import Course
from quizzes.models import Quiz
from questions.models import EmployeeProgress, MaterialProgress

def is_admin(user):
    return user.is_authenticated and (user.is_superuser or user.role == 'Admin')

@login_required
def admin_dashboard(request):
    if not is_admin(request.user):
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('employee_dashboard')
    
    # Get all necessary data for admin dashboard
    employees = CustomUser.objects.filter(role='Employee')
    courses = Course.objects.all().order_by('-id')  # Most recent first
    quizzes = Quiz.objects.all()
    
    # Calculate completion rate
    total_possible_completions = employees.count() * courses.count()
    completed_courses = EmployeeProgress.objects.filter(completed=True).count()
    completion_rate = (completed_courses / total_possible_completions * 100) if total_possible_completions > 0 else 0
    
    # Calculate completion by level
    completion_by_level = []
    for level in range(1, 4):
        level_courses = courses.filter(level=level)
        level_completions = EmployeeProgress.objects.filter(course__level=level, completed=True).count()
        total_possible = employees.count() * level_courses.count()
        level_rate = (level_completions / total_possible * 100) if total_possible > 0 else 0
        completion_by_level.append({
            'level': level,
            'rate': level_rate
        })
    
    context = {
        'employees': employees,
        'courses': courses,
        'quizzes': quizzes,
        'completion_rate': round(completion_rate, 1),
        'completion_by_level': completion_by_level,
    }
    
    return render(request, 'dashboard/admin_dashboard.html', context)

@login_required
def employee_dashboard(request):
    user = request.user
    
    # Get current level courses with progress
    current_courses = Course.objects.filter(level=user.current_level)
    
    # Calculate progress for each course
    for course in current_courses:
        total_materials = course.videos.count() + course.pdfs.count()
        completed_materials = MaterialProgress.objects.filter(
            employee=user,
            course=course,
            completed=True
        ).count()
        
        course.progress = (completed_materials / total_materials * 100) if total_materials > 0 else 0
        course.completed = EmployeeProgress.objects.filter(
            employee=user,
            course=course,
            completed=True
        ).exists()
        
        # Check if quiz is available (80% materials completed)
        course.quiz_available = course.progress >= 80

    # Calculate level progress
    total_level_courses = current_courses.count()
    completed_level_courses = EmployeeProgress.objects.filter(
        employee=user,
        course__in=current_courses,
        completed=True
    ).count()
    level_progress = (completed_level_courses / total_level_courses * 100) if total_level_courses > 0 else 0

    # Get next level preview if not at max level
    next_level_courses = []
    if user.current_level < 3:
        next_level_courses = Course.objects.filter(level=user.current_level + 1)

    context = {
        'user': user,
        'courses': current_courses,
        'available_courses': current_courses.count(),
        'completed_courses': completed_level_courses,
        'level_progress': level_progress,
        'next_level_courses': next_level_courses
    }
    
    return render(request, 'dashboard/employee_dashboard.html', context)

def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        confirm_password = request.POST.get('confirm_password')
        role = request.POST['role']

        # Validate passwords match
        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'registration/signup.html')

        # Validate password strength
        if len(password) < 8:
            messages.error(request, 'Password must be at least 8 characters long.')
            return render(request, 'registration/signup.html')

        try:
            # Check username availability
            if CustomUser.objects.filter(username=username).exists():
                messages.error(request, 'Username already exists.')
                return render(request, 'registration/signup.html')
            
            # Validate role
            if role not in ['Admin', 'Employee']:
                messages.error(request, 'Invalid role selected.')
                return render(request, 'registration/signup.html')
            
            # Create user with appropriate initial settings
            user = CustomUser.objects.create_user(
                username=username, 
                password=password,
                role=role,
                current_level=1 if role == 'Employee' else 3  # Admins start at max level
            )
            
            login(request, user)
            messages.success(request, f'Welcome {username}! Your account has been created successfully.')
            return redirect('admin_dashboard' if role == 'Admin' else 'employee_dashboard')
            
        except Exception as e:
            messages.error(request, f'Error creating account: {str(e)}')
            return render(request, 'registration/signup.html')
            
    return render(request, 'registration/signup.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {username}!')
            return redirect('admin_dashboard' if user.role == 'Admin' else 'employee_dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'registration/login.html')

def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login')