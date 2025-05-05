from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Course
from users.models import CustomUser
from django import forms

def is_employee(user):
    return user.is_authenticated and user.role == 'Employee'

def is_admin(user):
    return user.is_authenticated and user.role == 'Admin'

@login_required
def course_list(request):
    if request.user.role == 'Admin':
        courses = Course.objects.all()
    else:
        courses = Course.objects.filter(level=request.user.current_level)
    return render(request, 'course_list.html', {'courses': courses})

@login_required
def course_detail(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if not is_admin(request.user) and course.level != request.user.current_level:
        messages.error(request, 'Access denied. This course is not for your current level.')
        return redirect('course_list')
    return render(request, 'course_detail.html', {'course': course})

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'desc', 'level']

@login_required
@user_passes_test(is_admin)
def course_create(request):
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            course.user = request.user
            course.save()
            return redirect('course_list')
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
            form.save()
            return redirect('course_list')
    else:
        form = CourseForm(instance=course)
    return render(request, 'course_form.html', {'form': form, 'course': course})

@login_required
@user_passes_test(is_admin)
def course_delete(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.method == 'POST':
        course.delete()
        return redirect('course_list')
    return render(request, 'course_detail.html', {'course': course})