from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, Http404, FileResponse
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.contrib.auth.models import User
from .models import Student, Course, Enrollment, FileUpload
from .forms import StudentRegistrationForm, CourseEnrollmentForm, FileUploadForm, StudentProfileForm
import os


def home(request):
    """Home page view"""
    if request.user.is_authenticated:
        return redirect('students:dashboard')
    return render(request, 'students/home.html')


# def register(request):
#     """Student registration view"""
#     if request.method == 'POST':
#         form = StudentRegistrationForm(request.POST)
#         if form.is_valid():
#             user = form.save()
#             username = form.cleaned_data.get('username')
#             messages.success(request, f'Account created for {username}! You can now log in.')
#             return redirect('students:login')
#     else:
#         form = StudentRegistrationForm()
    
#     return render(request, 'students/register.html', {'form': form})


def register(request):
    """Student registration view"""
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                username = user.username
                messages.success(request, f'Account created for {username}! You can now log in.')
                return redirect('students:login')
            except Exception as e:
                messages.error(request, f'Registration failed: {e}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = StudentRegistrationForm()
    
    return render(request, 'students/register.html', {'form': form})

def login_view(request):
    """Login view"""
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
            return redirect('students:dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'students/login.html')


def logout_view(request):
    """Logout view"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('students:login')


@login_required
def dashboard(request):
    """Dashboard view for students and staff"""
    context = {}
    
    if request.user.is_staff:
        # Admin dashboard
        context.update({
            'is_admin': True,
            'total_students': Student.objects.count(),
            'total_courses': Course.objects.count(),
            'total_enrollments': Enrollment.objects.filter(is_active=True).count(),
            'total_files': FileUpload.objects.count(),
            'recent_enrollments': Enrollment.objects.select_related('student__user', 'course').order_by('-enrollment_date')[:5],
            'recent_files': FileUpload.objects.select_related('uploaded_by', 'course').order_by('-timestamp')[:5],
        })
    else:
        # Student dashboard
        try:
            student = request.user.student
            enrollments = Enrollment.objects.filter(student=student, is_active=True).select_related('course')
            context.update({
                'is_admin': False,
                'student': student,
                'enrollments': enrollments,
                'enrolled_courses_count': enrollments.count(),
                'can_enroll_more': student.can_enroll_in_course(),
                'recent_files': FileUpload.objects.filter(
                    course__in=[e.course for e in enrollments]
                ).select_related('uploaded_by', 'course').order_by('-timestamp')[:5],
            })
        except Student.DoesNotExist:
            messages.error(request, 'Student profile not found. Please contact admin.')
            return redirect('students:logout')
    
    return render(request, 'students/dashboard.html', context)


@login_required
def course_list(request):
    """List all available courses"""
    courses = Course.objects.filter(is_active=True).order_by('course_code')
    
    # Add enrollment status for each course if user is a student
    if not request.user.is_staff and hasattr(request.user, 'student'):
        enrolled_courses = Enrollment.objects.filter(
            student=request.user.student, is_active=True
        ).values_list('course_id', flat=True)
        
        for course in courses:
            course.is_enrolled = course.id in enrolled_courses
            course.can_enroll_now = course.can_enroll() and not course.is_enrolled
    
    return render(request, 'students/course_list.html', {'courses': courses})


@login_required
def course_detail(request, course_id):
    """Course detail view"""
    course = get_object_or_404(Course, id=course_id, is_active=True)
    
    # Get enrolled students
    enrollments = Enrollment.objects.filter(course=course, is_active=True).select_related('student__user')
    
    # Check if current user is enrolled
    is_enrolled = False
    if hasattr(request.user, 'student'):
        is_enrolled = Enrollment.objects.filter(
            student=request.user.student, course=course, is_active=True
        ).exists()
    
    # Get course files
    files = FileUpload.objects.filter(course=course).select_related('uploaded_by').order_by('-timestamp')
    
    context = {
        'course': course,
        'enrollments': enrollments,
        'is_enrolled': is_enrolled,
        'files': files,
        'can_enroll': course.can_enroll() and not is_enrolled and hasattr(request.user, 'student'),
    }
    
    return render(request, 'students/course_detail.html', context)


@login_required
def enroll_course(request, course_id):
    """Enroll in a course"""
    course = get_object_or_404(Course, id=course_id, is_active=True)
    
    # Check if user is a student
    if not hasattr(request.user, 'student'):
        messages.error(request, 'Only students can enroll in courses.')
        return redirect('students:course_detail', course_id=course_id)
    
    student = request.user.student
    
    # Check if already enrolled
    if Enrollment.objects.filter(student=student, course=course, is_active=True).exists():
        messages.warning(request, 'You are already enrolled in this course.')
        return redirect('students:course_detail', course_id=course_id)
    
    # Check enrollment limits
    if not student.can_enroll_in_course():
        messages.error(request, 'You cannot enroll in more than 5 courses.')
        return redirect('students:course_detail', course_id=course_id)
    
    if not course.can_enroll():
        messages.error(request, 'This course is full.')
        return redirect('students:course_detail', course_id=course_id)
    
    # Create enrollment
    try:
        enrollment = Enrollment.objects.create(student=student, course=course)
        messages.success(request, f'You have successfully enrolled in {course.title}!')
    except ValidationError as e:
        messages.error(request, str(e))
    
    return redirect('students:course_detail', course_id=course_id)


@login_required
def unenroll_course(request, course_id):
    """Unenroll from a course"""
    course = get_object_or_404(Course, id=course_id)
    
    if not hasattr(request.user, 'student'):
        messages.error(request, 'Only students can unenroll from courses.')
        return redirect('students:course_detail', course_id=course_id)
    
    student = request.user.student
    
    try:
        enrollment = Enrollment.objects.get(student=student, course=course, is_active=True)
        enrollment.is_active = False
        enrollment.save()
        messages.success(request, f'You have successfully unenrolled from {course.title}.')
    except Enrollment.DoesNotExist:
        messages.error(request, 'You are not enrolled in this course.')
    
    return redirect('students:dashboard')


@login_required
def upload_file(request):
    """Upload file to a course"""
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            file_upload = form.save(commit=False)
            file_upload.uploaded_by = request.user
            file_upload.save()
            messages.success(request, 'File uploaded successfully!')
            return redirect('students:course_detail', course_id=file_upload.course.id)
    else:
        form = FileUploadForm(user=request.user)
    
    return render(request, 'students/upload_file.html', {'form': form})


@login_required
def download_file(request, file_id):
    """Download a file"""
    file_upload = get_object_or_404(FileUpload, id=file_id)
    
    # Check if user can access this file
    can_access = False
    if request.user.is_staff:
        can_access = True
    elif hasattr(request.user, 'student'):
        # Student can access files from courses they're enrolled in
        is_enrolled = Enrollment.objects.filter(
            student=request.user.student, course=file_upload.course, is_active=True
        ).exists()
        can_access = is_enrolled
    
    if not can_access:
        messages.error(request, 'You do not have permission to access this file.')
        return redirect('students:dashboard')
    
    try:
        response = FileResponse(
            file_upload.file.open(),
            as_attachment=True,
            filename=file_upload.file_name
        )
        return response
    except FileNotFoundError:
        messages.error(request, 'File not found.')
        return redirect('students:dashboard')


@login_required
def delete_file(request, file_id):
    """Delete a file"""
    file_upload = get_object_or_404(FileUpload, id=file_id)
    
    # Check if user can delete this file
    if not file_upload.can_delete(request.user):
        messages.error(request, 'You do not have permission to delete this file.')
        return redirect('students:course_detail', course_id=file_upload.course.id)
    
    if request.method == 'POST':
        course_id = file_upload.course.id
        file_name = file_upload.file_name
        
        # Delete the actual file
        if file_upload.file:
            if os.path.exists(file_upload.file.path):
                os.remove(file_upload.file.path)
        
        # Delete the database record
        file_upload.delete()
        messages.success(request, f'File "{file_name}" deleted successfully.')
        return redirect('students:course_detail', course_id=course_id)
    
    return render(request, 'students/delete_file.html', {'file_upload': file_upload})


@login_required
def profile(request):
    """User profile view"""
    if not hasattr(request.user, 'student'):
        messages.error(request, 'Student profile not found.')
        return redirect('students:dashboard')
    
    student = request.user.student
    
    if request.method == 'POST':
        form = StudentProfileForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('students:profile')
    else:
        form = StudentProfileForm(instance=student)
    
    return render(request, 'students/profile.html', {'form': form, 'student': student})


@login_required
def my_courses(request):
    """View student's enrolled courses"""
    if not hasattr(request.user, 'student'):
        messages.error(request, 'Student profile not found.')
        return redirect('students:dashboard')
    
    student = request.user.student
    enrollments = Enrollment.objects.filter(student=student, is_active=True).select_related('course')
    
    return render(request, 'students/my_courses.html', {'enrollments': enrollments, 'student': student})


@login_required
def my_files(request):
    """View files uploaded by the user"""
    files = FileUpload.objects.filter(uploaded_by=request.user).select_related('course').order_by('-timestamp')
    
    return render(request, 'students/my_files.html', {'files': files})


def search_courses(request):
    """Search courses"""
    query = request.GET.get('q', '')
    courses = Course.objects.filter(is_active=True)
    
    if query:
        courses = courses.filter(
            Q(title__icontains=query) |
            Q(course_code__icontains=query) |
            Q(instructor__icontains=query) |
            Q(description__icontains=query)
        )
    
    return render(request, 'students/search_results.html', {'courses': courses, 'query': query})