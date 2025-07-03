from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Student


@receiver(post_save, sender=User)
def create_or_update_student_profile(sender, instance, created, **kwargs):
    """Create or update student profile when user is created/updated"""
    if created and not instance.is_staff:
        # Only create student profile for non-staff users
        # and only if it doesn't exist already
        if not hasattr(instance, 'student'):
            Student.objects.create(
                user=instance,
                student_id=f"STU{instance.id:06d}"  # Auto-generate student ID
            )