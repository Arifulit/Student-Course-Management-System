from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class Student(models.Model):
    """Student profile model linked to Django's User model"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    student_id = models.CharField(max_length=20, unique=True)
    phone = models.CharField(max_length=15, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} ({self.student_id})"

    def can_enroll_in_course(self):
        """Check if student can enroll in more courses (max 5)"""
        return self.enrollment_set.count() < 5

    class Meta:
        ordering = ['student_id']


class Course(models.Model):
    """Course model"""
    course_code = models.CharField(max_length=10, unique=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    instructor = models.CharField(max_length=100)
    credits = models.IntegerField(default=3)
    max_students = models.IntegerField(default=30)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.course_code} - {self.title}"

    def enrolled_students_count(self):
        """Get count of enrolled students"""
        return self.enrollment_set.count()

    def can_enroll(self):
        """Check if course has space for more students"""
        return self.enrolled_students_count() < self.max_students

    class Meta:
        ordering = ['course_code']


class Enrollment(models.Model):
    """Enrollment model linking Student and Course"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    enrollment_date = models.DateTimeField(auto_now_add=True)
    grade = models.CharField(max_length=2, blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ['student', 'course']
        ordering = ['-enrollment_date']

    def __str__(self):
        return f"{self.student.user.username} enrolled in {self.course.course_code}"

    def save(self, *args, **kwargs):
        # Check if student can enroll in more courses
        if not self.pk and not self.student.can_enroll_in_course():
            raise ValidationError("Student cannot enroll in more than 5 courses")
        
        # Check if course has space
        if not self.pk and not self.course.can_enroll():
            raise ValidationError("Course is full")
        
        super().save(*args, **kwargs)


class FileUpload(models.Model):
    """File upload model for course materials"""
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    file = models.FileField(upload_to='course_files/')
    file_name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    file_type = models.CharField(max_length=10, blank=True)
    file_size = models.BigIntegerField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.file_name} - {self.course.course_code}"

    def save(self, *args, **kwargs):
        if self.file:
            self.file_name = self.file.name
            self.file_size = self.file.size
            # Get file extension
            import os
            self.file_type = os.path.splitext(self.file.name)[1][1:].lower()
        super().save(*args, **kwargs)

    def can_delete(self, user):
        """Check if user can delete this file"""
        return user == self.uploaded_by or user.is_staff

    class Meta:
        ordering = ['-timestamp']