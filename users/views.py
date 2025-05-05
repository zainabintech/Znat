from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Avg
from .models import CustomUser
from courses.models import Course
from quizzes.models import Quiz
from questions.models import EmployeeProgress

def is_admin(user):
    return user.is_authenticated and user.role == 'Admin'

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
        completion_by_level.append(level_rate)
    
    # Calculate average quiz scores over time
    quiz_scores = []
    quiz_labels = []
    recent_quizzes = quizzes.order_by('-id')[:10]  # Last 10 quizzes
    for quiz in recent_quizzes:
        avg_score = EmployeeProgress.objects.filter(course=quiz.course).aggregate(Avg('quiz_score'))['quiz_score__avg']
        if avg_score:
            quiz_scores.append(float(avg_score))
            quiz_labels.append(quiz.course.title[:10] + '...')  # Truncate long titles
    
    # Calculate completion percentage for each employee
    for employee in employees:
        completed = EmployeeProgress.objects.filter(employee=employee, completed=True).count()
        total = courses.filter(level__lte=employee.current_level).count()
        employee.completion_percentage = (completed / total * 100) if total > 0 else 0
    
    context = {
        'employees': employees,
        'courses': courses,
        'quizzes': quizzes,
        'total_employees': employees.count(),
        'total_courses': courses.count(),
        'total_quizzes': quizzes.count(),
        'completion_rate': completion_rate,
        'completion_by_level': completion_by_level,
        'quiz_scores': quiz_scores,
        'quiz_labels': quiz_labels,
    }
    return render(request, 'dashboard/admin_dashboard.html', context)

@login_required
def employee_dashboard(request):
    user = request.user
    # Get employee specific courses based on their level
    courses = Course.objects.filter(level=user.current_level)
    context = {
        'user': user,
        'courses': courses,
        'completed_courses': courses.filter(employeeprogress__employee=user, employeeprogress__completed=True).count()
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