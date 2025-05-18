from django.db import models
from django.contrib.auth.models import User
from a_classroom.models import Subject
import random
import string

class Activity(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='activities')
    activity_id = models.CharField(max_length=8, unique=True, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    max_score = models.PositiveIntegerField(default=100)
    created_at = models.DateTimeField(auto_now_add=True)
    due_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_archived = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.activity_id:
            self.activity_id = self.generate_unique_activity_id()
        super().save(*args, **kwargs)

    @staticmethod
    def generate_unique_activity_id():
        characters = string.ascii_uppercase + string.digits
        while True:
            unique_id = ''.join(random.choices(characters, k=8))
            if not Activity.objects.filter(activity_id=unique_id).exists():
                return unique_id

class ActivitySubmission(models.Model):
    student = models.ForeignKey(User, verbose_name="STUDENT", on_delete=models.CASCADE, related_name='activity_submissions')
    activity = models.ForeignKey(Activity, verbose_name="ACTIVITY", on_delete=models.CASCADE, related_name='submissions')
    submitted_code = models.TextField(verbose_name="SUBMITTED CODE", default="")
    submitted_at = models.DateTimeField(auto_now_add=True, verbose_name="SUBMITTED AT")
    feedback = models.CharField(max_length = 100, null = True)
    score = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        unique_together = ('student', 'activity')

class ActivityExample(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name='examples')
    example_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)