from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from b_enrollment.models import UserProfile, Role
import re
from django.core.mail import send_mail
from django.conf import settings


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        role = Role.INSTRUCTOR
        if instance.is_staff or instance.is_superuser:
            role = Role.ADMIN
        elif re.search(r'\d', instance.email):
            role = Role.STUDENT

        if not instance.has_usable_password():
            instance.set_password("123")
            instance.save(update_fields=["password"])

        UserProfile.objects.create(user=instance, role=role)


        instance.is_active = False
        instance.save(update_fields=["is_active"])

        try:
            subject = "Account Pending Activation - CodeCheckAI"
            message = (
                f"Hello {instance.first_name},\n\n"
                "Thank you for signing up for CodeCheckAI.\n\n"
                "Your account is currently inactive. Please wait for the admin to review and activate your account.\n\n"
                "You will receive another email once your account is approved.\n\n"
                "If you have any questions, feel free to contact support.\n\n"
                "Best regards,\nCodeCheckAI Team"
            )
            send_mail(subject, message, settings.EMAIL_HOST_USER, [instance.email])
            print("✅ Email verification sent successfully!")
        except Exception as e:
            print(f"❌ Error sending verification email: {e}")
