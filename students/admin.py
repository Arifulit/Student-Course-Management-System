from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Student, Course, Enrollment, FileUpload


# Inline admin for Student in User admin
class StudentInline(admin.StackedInline):
    model = Student
    can_delete = False
    verbose_name_plural = 'Student Profile'


# Extended User Admin
class ExtendedUserAdmin(UserAdmin):
    inlines = (StudentInline,)


# Re-register User with extended admin
admin.site.unregister(User)
admin.site.register(User, ExtendedUserAdmin)


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['student_id', 'user', 'phone', 'created_at']
    list_filter = ['created_at']
    search_fields = ['student_id', 'user__username', 'user__email', 'user__first_name', 'user__last_name']
    ordering = ['student_id']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['course_code', 'title', 'instructor', 'credits', 'max_students', 'enrolled_students_count', 'is_active']
    list_filter = ['is_active', 'credits', 'created_at']
    search_fields = ['course_code', 'title', 'instructor']
    ordering = ['course_code']
    readonly_fields = ['created_at', 'updated_at']

    def enrolled_students_count(self, obj):
        return obj.enrolled_students_count()
    enrolled_students_count.short_description = 'Enrolled Students'


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'enrollment_date', 'grade', 'is_active']
    list_filter = ['enrollment_date', 'is_active', 'course']
    search_fields = ['student__user__username', 'student__student_id', 'course__course_code', 'course__title']
    ordering = ['-enrollment_date']
    readonly_fields = ['enrollment_date']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('student__user', 'course')


@admin.register(FileUpload)
class FileUploadAdmin(admin.ModelAdmin):
    list_display = ['file_name', 'course', 'uploaded_by', 'file_type', 'file_size_mb', 'timestamp']
    list_filter = ['file_type', 'timestamp', 'course']
    search_fields = ['file_name', 'course__course_code', 'uploaded_by__username']
    ordering = ['-timestamp']
    readonly_fields = ['timestamp', 'file_size', 'file_type']

    def file_size_mb(self, obj):
        return f"{obj.file_size / (1024*1024):.2f} MB"
    file_size_mb.short_description = 'File Size'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('uploaded_by', 'course')


# Customize admin site headers
admin.site.site_header = "Course Management System"
admin.site.site_title = "Course Management Admin"
admin.site.index_title = "Welcome to Course Management Administration"