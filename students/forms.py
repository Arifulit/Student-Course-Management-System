from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Student, Course, Enrollment, FileUpload


# class StudentRegistrationForm(UserCreationForm):
#     """Form for student registration"""
#     email = forms.EmailField(required=True)
#     first_name = forms.CharField(max_length=30, required=True)
#     last_name = forms.CharField(max_length=30, required=True)
#     student_id = forms.CharField(max_length=20, required=True)
#     phone = forms.CharField(max_length=15, required=False)
#     date_of_birth = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
#     address = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False)

#     class Meta:
#         model = User
#         fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         # Add CSS classes for styling
#         for field_name, field in self.fields.items():
#             field.widget.attrs['class'] = 'form-control'
#             if field_name == 'address':
#                 field.widget.attrs['class'] = 'form-control'
#                 field.widget.attrs['rows'] = 3

#     def clean_student_id(self):
#         student_id = self.cleaned_data['student_id']
#         if Student.objects.filter(student_id=student_id).exists():
#             raise forms.ValidationError("Student ID already exists.")
#         return student_id

#     def clean_email(self):
#         email = self.cleaned_data['email']
#         if User.objects.filter(email=email).exists():
#             raise forms.ValidationError("Email already exists.")
#         return email

#     def save(self, commit=True):
#         user = super().save(commit=False)
#         user.email = self.cleaned_data['email']
#         user.first_name = self.cleaned_data['first_name']
#         user.last_name = self.cleaned_data['last_name']
        
#         if commit:
#             user.save()
#             # Create Student profile
#             Student.objects.create(
#                 user=user,
#                 student_id=self.cleaned_data['student_id'],
#                 phone=self.cleaned_data.get('phone', ''),
#                 date_of_birth=self.cleaned_data.get('date_of_birth'),
#                 address=self.cleaned_data.get('address', '')
#             )
#         return user

class StudentRegistrationForm(UserCreationForm):
    """Form for student registration"""
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    student_id = forms.CharField(max_length=20, required=True)
    phone = forms.CharField(max_length=15, required=False)
    date_of_birth = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    address = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            if field_name == 'address':
                field.widget.attrs['rows'] = 3

    def clean_student_id(self):
        student_id = self.cleaned_data['student_id']
        if Student.objects.filter(student_id=student_id).exists():
            raise forms.ValidationError("Student ID already exists.")
        return student_id

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already exists.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
            # Safe student creation (avoids duplicate user_id)
            Student.objects.get_or_create(
                user=user,
                defaults={
                    'student_id': self.cleaned_data['student_id'],
                    'phone': self.cleaned_data.get('phone', ''),
                    'date_of_birth': self.cleaned_data.get('date_of_birth'),
                    'address': self.cleaned_data.get('address', '')
                }
            )
        return user


class CourseEnrollmentForm(forms.ModelForm):
    """Form for course enrollment"""
    
    class Meta:
        model = Enrollment
        fields = ['course']
        widgets = {
            'course': forms.Select(attrs={'class': 'form-control'})
        }

    def __init__(self, student=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.student = student
        
        # Only show courses that are active and not full
        available_courses = Course.objects.filter(is_active=True)
        
        # Exclude courses the student is already enrolled in
        if student:
            enrolled_courses = Enrollment.objects.filter(
                student=student, is_active=True
            ).values_list('course', flat=True)
            available_courses = available_courses.exclude(id__in=enrolled_courses)
        
        # Filter courses that are not full
        available_courses = [course for course in available_courses if course.can_enroll()]
        
        self.fields['course'].queryset = Course.objects.filter(
            id__in=[course.id for course in available_courses]
        )
        self.fields['course'].empty_label = "Select a course"

    def clean(self):
        cleaned_data = super().clean()
        course = cleaned_data.get('course')
        
        if self.student and course:
            # Check if student can enroll in more courses
            if not self.student.can_enroll_in_course():
                raise forms.ValidationError("You cannot enroll in more than 5 courses.")
            
            # Check if course has space
            if not course.can_enroll():
                raise forms.ValidationError("This course is full.")
            
            # Check if already enrolled
            if Enrollment.objects.filter(student=self.student, course=course, is_active=True).exists():
                raise forms.ValidationError("You are already enrolled in this course.")
        
        return cleaned_data


# class FileUploadForm(forms.ModelForm):
#     """Form for file uploads"""
    
#     class Meta:
#         model = FileUpload
#         fields = ['file', 'course', 'description']
#         widgets = {
#             'file': forms.FileInput(attrs={'class': 'form-control'}),
#             'course': forms.Select(attrs={'class': 'form-control'}),
#             'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
#         }

#     def __init__(self, user=None, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.user = user
        
#         # If user is a student, only show courses they're enrolled in
#         if user and hasattr(user, 'student'):
#             enrolled_courses = Enrollment.objects.filter(
#                 student=user.student, is_active=True
#             ).values_list('course', flat=True)
#             self.fields['course'].queryset = Course.objects.filter(id__in=enrolled_courses)
#         elif user and user.is_staff:
#             # Staff can upload to any course
#             self.fields['course'].queryset = Course.objects.filter(is_active=True)
#         else:
#             self.fields['course'].queryset = Course.objects.none()
        
#         self.fields['course'].empty_label = "Select a course"
#         self.fields['description'].required = False

#     def clean_file(self):
#         file = self.cleaned_data.get('file')
#         if file:
#             # Check file size (max 10MB)
#             if file.size > 10 * 1024 * 1024:
#                 raise forms.ValidationError("File size cannot exceed 10MB.")
#         return file


class FileUploadForm(forms.ModelForm):
    """Form for uploading files to courses"""

    class Meta:
        model = FileUpload
        fields = ['file', 'course', 'description']
        widgets = {
            'file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'course': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

        # Dynamically filter course choices
        if user and hasattr(user, 'student'):
            # Only show courses the student is enrolled in and active
            enrolled_courses = Enrollment.objects.filter(
                student=user.student, is_active=True
            ).values_list('course_id', flat=True)
            self.fields['course'].queryset = Course.objects.filter(
                id__in=enrolled_courses, is_active=True
            )
        elif user and user.is_staff:
            # Staff can upload to any active course
            self.fields['course'].queryset = Course.objects.filter(is_active=True)
        else:
            # Other users get no options
            self.fields['course'].queryset = Course.objects.none()

        self.fields['course'].empty_label = "Select a course"
        self.fields['description'].required = False

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            if file.size > 10 * 1024 * 1024:  # 10 MB
                raise forms.ValidationError("File size cannot exceed 10MB.")
        return file


class StudentProfileForm(forms.ModelForm):
    """Form for updating student profile"""
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True)
    
    class Meta:
        model = Student
        fields = ['phone', 'date_of_birth', 'address']
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add CSS classes
        for field_name, field in self.fields.items():
            if field_name not in ['date_of_birth', 'address', 'phone']:
                field.widget.attrs['class'] = 'form-control'
        
        # Pre-populate User fields if instance exists
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email

    def save(self, commit=True):
        student = super().save(commit=False)
        
        # Update User fields
        if student.user:
            student.user.first_name = self.cleaned_data['first_name']
            student.user.last_name = self.cleaned_data['last_name']
            student.user.email = self.cleaned_data['email']
            if commit:
                student.user.save()
        
        if commit:
            student.save()
        
        return student