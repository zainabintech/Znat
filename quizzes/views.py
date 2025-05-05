from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Quiz
from courses.models import Course
from users.models import CustomUser
from questions.models import Question

def is_admin(user):
    return user.is_authenticated and user.role == 'Admin'

@login_required
@user_passes_test(is_admin)
def quiz_create(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    if request.method == 'POST':
        passing_score = request.POST['passing_score']
        quiz = Quiz(course=course, passing_score=passing_score, user=request.user)
        quiz.save()
        return redirect('course_list')
    return render(request, 'quiz_form.html', {'course': course})

@login_required
@user_passes_test(is_admin)
def quiz_detail(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk)
    questions = Question.objects.filter(quiz=quiz)
    return render(request, 'quiz_detail.html', {'quiz': quiz, 'questions': questions})

@login_required
@user_passes_test(is_admin)
def quiz_list(request):
    quizzes = Quiz.objects.all()
    return render(request, 'quiz_list.html', {'quizzes': quizzes})

@login_required
def quiz_take(request, pk):
    if request.user.role != 'Employee':
        return redirect('admin_dashboard')
    quiz = get_object_or_404(Quiz, pk=pk)
    questions = Question.objects.filter(quiz=quiz)
    if request.method == 'POST':
        score = 0
        total = questions.count()
        feedback = []
        for question in questions:
            user_answer = request.POST.get(f'question_{question.id}')
            is_correct = user_answer and int(user_answer) == question.correct_option_id
            if is_correct:
                score += 1
            feedback.append({
                'text': question.text,
                'is_correct': is_correct,
                'user_answer': user_answer,
                'correct_answer': question.correct_option_id
            })
        final_score = (score / total) * 100 if total > 0 else 0
        request.user.latest_score = final_score
        if final_score >= quiz.passing_score:
            request.user.current_level = min(request.user.current_level + 1, 3)
        request.user.save()
        return render(request, 'quiz_result.html', {
            'quiz': quiz,
            'score': final_score,
            'passing_score': quiz.passing_score,
            'feedback': feedback,
            'passed': final_score >= quiz.passing_score
        })
    return render(request, 'quiz_take.html', {'quiz': quiz, 'questions': questions})

@login_required
def quiz_result(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk)
    if request.user.role != 'Employee':
        return redirect('admin_dashboard')
    
    # Get the user's latest attempt for this quiz
    latest_score = request.user.latest_score
    
    return render(request, 'quiz_result.html', {
        'quiz': quiz,
        'score': latest_score,
        'passing_score': quiz.passing_score,
        'passed': latest_score >= quiz.passing_score if latest_score is not None else False
    })