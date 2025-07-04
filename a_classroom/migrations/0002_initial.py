# Generated by Django 5.2 on 2025-04-26 10:43

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('a_classroom', '0001_initial'),
        ('b_enrollment', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='subject',
            name='students',
            field=models.ManyToManyField(blank=True, related_name='joined_subjects', through='b_enrollment.StudentSubject', to=settings.AUTH_USER_MODEL),
        ),
    ]
