from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.files.storage import default_storage
from django.db import transaction
from .models import Course, Video, PDF, QuizQuestion, EmployeeProgress, Quiz, Question
from .forms import VideoForm, PDFForm, QuizQuestionForm
import os
import magic

def is_admin(user):
    return user.is_authenticated and user.role == 'Admin'

def validate_file_type(file, content_type_prefix):
    mime = magic.from_buffer(file.read(1024), mime=True)
    file.seek(0)  # Reset file pointer
    if not mime.startswith(content_type_prefix):
        raise ValidationError(f'Invalid file type. Expected {content_type_prefix}, got {mime}')

@login_required
@user_passes_test(is_admin)
def question_create(request, quiz_id):
    quiz = get_object_or_404(Quiz, pk=quiz_id)
    if request.method == 'POST':
        text = request.POST['text']
        correct_option_id = request.POST['correct_option_id']
        type = request.POST['type']
        question = Question(quiz=quiz, text=text, correct_option_id=correct_option_id, type=type)
        question.save()
        return redirect('quiz_list')
    return render(request, 'question_form.html', {'quiz': quiz})

@login_required
@user_passes_test(is_admin)
def upload_course_material(request):
    if request.method == 'POST':
        material_type = request.POST.get('material_type')
        title = request.POST.get('title')
        course_id = request.POST.get('course')
        
        try:
            with transaction.atomic():
                course = Course.objects.get(pk=course_id)
                
                if material_type == 'video':
                    youtube_url = request.POST.get('youtube_url')
                    if not youtube_url:
                        raise ValidationError('Please provide a YouTube URL')
                    
                    # Create video
                    video = Video.objects.create(
                        title=title,
                        course=course,
                        youtube_url=youtube_url
                    )
                    messages.success(request, 'Video added successfully')
                    
                elif material_type == 'pdf':
                    if 'pdf_file' not in request.FILES:
                        raise ValidationError('No PDF file uploaded')
                    
                    pdf_file = request.FILES['pdf_file']
                    validate_file_type(pdf_file, 'application/pdf')
                    
                    # Check file size (10MB limit)
                    if pdf_file.size > 10485760:
                        raise ValidationError('PDF file too large (max 10MB)')
                    
                    pdf = PDF.objects.create(
                        title=title,
                        course=course,
                        pdf_file=pdf_file
                    )
                    messages.success(request, 'PDF uploaded successfully')
                    
                elif request.POST.get('action') == 'delete_video':
                    video_id = request.POST.get('id')
                    video = get_object_or_404(Video, id=video_id)
                    video.delete()
                    messages.success(request, 'Video deleted successfully')
                    
                elif request.POST.get('action') == 'delete_pdf':
                    pdf_id = request.POST.get('id')
                    pdf = get_object_or_404(PDF, id=pdf_id)
                    if pdf.pdf_file:
                        try:
                            if os.path.exists(pdf.pdf_file.path):
                                default_storage.delete(pdf.pdf_file.path)
                        except Exception as e:
                            messages.warning(request, f'Error deleting file: {str(e)}')
                    pdf.delete()
                    messages.success(request, 'PDF deleted successfully')
                
        except ValidationError as e:
            messages.error(request, str(e))
        except Course.DoesNotExist:
            messages.error(request, 'Selected course does not exist')
        except Exception as e:
            messages.error(request, f'Error processing upload: {str(e)}')
    
    # Get current course if in wizard flow
    course = None
    if 'course_id' in request.GET:
        course = get_object_or_404(Course, pk=request.GET.get('course_id'))
    
    # Show all courses and materials
    if course:
        videos = Video.objects.filter(course=course).select_related('course')
        pdfs = PDF.objects.filter(course=course).select_related('course')
    else:
        videos = Video.objects.all().select_related('course')
        pdfs = PDF.objects.all().select_related('course')
    
    context = {
        'course': course,
        'courses': Course.objects.all().order_by('level', 'title'),
        'videos': videos,
        'pdfs': pdfs,
    }
    return render(request, 'upload_course_material.html', context)

@user_passes_test(is_admin)
def create_quiz_question(request):
    if request.method == 'POST':
        form = QuizQuestionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin_dashboard')
    else:
        form = QuizQuestionForm()
    return render(request, 'create_quiz_question.html', {'form': form})

@login_required
def take_quiz(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    questions = course.quiz_questions.all()
    if request.method == 'POST':
        score = 0
        for question in questions:
            selected_option = request.POST.get(str(question.id))
            if selected_option == question.correct_option:
                score += 1
        progress, created = EmployeeProgress.objects.get_or_create(employee=request.user, course=course)
        progress.quiz_score = score
        progress.completed = score >= len(questions) * 0.7  # Pass if 70% correct
        progress.save()
        return render(request, 'quiz_result.html', {'score': score, 'passed': progress.completed})
    return render(request, 'take_quiz.html', {'course': course, 'questions': questions})

@login_required
def quiz_questions_list(request, quiz_id):
    quiz = get_object_or_404(Quiz, pk=quiz_id)
    questions = Question.objects.filter(quiz=quiz)
    return render(request, 'questions/quiz_questions_list.html', {
        'quiz': quiz,
        'questions': questions
    })

@login_required
def quiz_question_detail(request, quiz_id, question_id):
    quiz = get_object_or_404(Quiz, pk=quiz_id)
    question = get_object_or_404(Question, pk=question_id, quiz=quiz)
    return render(request, 'questions/quiz_question_detail.html', {
        'quiz': quiz,
        'question': question
    })
