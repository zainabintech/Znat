from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Count, Q
from django.db import transaction
from .models import Quiz
from courses.models import Course
from users.models import CustomUser
from questions.models import Question, MaterialProgress, EmployeeProgress
from datetime import datetime

def is_admin(user):
    return user.is_authenticated and user.role == 'Admin'

@login_required
@user_passes_test(is_admin)
def quiz_create(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    if request.method == 'POST':
        try:
            with transaction.atomic():
                quiz = Quiz.objects.create(
                    course=course,
                    passing_score=float(request.POST.get('passing_score', 70)),
                    user=request.user
                )
                messages.success(request, 'Quiz created successfully')
                return redirect('question_create', quiz_id=quiz.id)
        except Exception as e:
            messages.error(request, f'Error creating quiz: {str(e)}')
    return render(request, 'quiz_form.html', {'course': course})

@login_required
def quiz_list(request):
    if request.user.is_admin():
        quizzes = Quiz.objects.all().select_related('course', 'user')
    else:
        # For employees, show only quizzes for their current level
        quizzes = Quiz.objects.filter(
            course__level=request.user.current_level
        ).select_related('course', 'user')
        
    context = {
        'quizzes': quizzes,
        'is_admin': request.user.is_admin()
    }
    return render(request, 'quiz_list.html', context)

@login_required
@user_passes_test(is_admin)
def quiz_detail(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk)
    questions = Question.objects.filter(quiz=quiz)
    total_attempts = EmployeeProgress.objects.filter(course=quiz.course).count()
    passing_attempts = EmployeeProgress.objects.filter(
        course=quiz.course,
        completed=True
    ).count()
    
    context = {
        'quiz': quiz,
        'questions': questions,
        'total_attempts': total_attempts,
        'passing_attempts': passing_attempts
    }
    return render(request, 'quiz_detail.html', context)

@login_required
def quiz_take(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk)
    
    # Verify user can take this quiz
    if not request.user.is_admin():
        # Only check level access
        if quiz.course.level != request.user.current_level:
            messages.error(request, 'You cannot access quizzes from other levels')
            return redirect('quiz_list')
            
        # Check course prerequisites
        if not quiz.course.is_available_for_user(request.user):
            messages.error(request, 'Complete the course prerequisites first')
            return redirect('course_detail', pk=quiz.course.id)
        
        # Remove material completion check
    
    questions = Question.objects.filter(quiz=quiz)
    
    if request.method == 'POST':
        score = 0
        total_questions = questions.count()
        
        if total_questions == 0:
            messages.error(request, 'This quiz has no questions')
            return redirect('quiz_list')
        
        try:
            with transaction.atomic():
                for question in questions:
                    answer = request.POST.get(f'question_{question.id}')
                    if answer and int(answer) == question.correct_option_id:
                        score += 1
                
                percentage_score = (score / total_questions) * 100
                
                # Update progress
                progress, created = EmployeeProgress.objects.get_or_create(
                    employee=request.user,
                    course=quiz.course
                )
                progress.quiz_score = percentage_score
                progress.completed = percentage_score >= quiz.passing_score
                progress.save()
                
                # Update user's latest score
                request.user.latest_score = percentage_score
                request.user.save()
                
                # If passed and not already at max level, enable next level
                if progress.completed and request.user.current_level < 3:
                    last_course = Course.objects.filter(
                        level=request.user.current_level
                    ).first()
                    if last_course and quiz.course == last_course:
                        request.user.current_level += 1
                        request.user.save()
                        messages.success(
                            request,
                            f'Congratulations! You\'ve unlocked level {request.user.current_level}'
                        )
                
                return render(request, 'quiz_result.html', {
                    'quiz': quiz,
                    'score': percentage_score,
                    'passed': progress.completed,
                    'required_score': quiz.passing_score
                })
                
        except Exception as e:
            messages.error(request, f'Error processing quiz: {str(e)}')
            return redirect('quiz_list')
    
    return render(request, 'quiz_take.html', {
        'quiz': quiz,
        'questions': questions
    })

@login_required
def quiz_result(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk)
    
    if not request.user.is_admin() and quiz.course.level != request.user.current_level:
        messages.error(request, 'You cannot access quiz results from other levels')
        return redirect('quiz_list')
    
    progress = EmployeeProgress.objects.filter(
        employee=request.user,
        course=quiz.course
    ).first()
    
    if not progress:
        messages.warning(request, 'No quiz attempt found')
        return redirect('quiz_list')
    
    return render(request, 'quiz_result.html', {
        'quiz': quiz,
        'score': progress.quiz_score,
        'passed': progress.completed,
        'required_score': quiz.passing_score
    })