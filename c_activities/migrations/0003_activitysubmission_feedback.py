# Generated by Django 5.2 on 2025-05-18 07:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('c_activities', '0002_activityexample'),
    ]

    operations = [
        migrations.AddField(
            model_name='activitysubmission',
            name='feedback',
            field=models.CharField(max_length=100, null=True),
        ),
    ]
