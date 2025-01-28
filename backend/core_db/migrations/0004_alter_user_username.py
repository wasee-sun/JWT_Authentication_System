# Generated by Django 5.1.5 on 2025-01-28 19:42

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core_db', '0003_alter_user_profile_img_alter_user_username'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(blank=True, max_length=255, null=True, unique=True, validators=[django.core.validators.RegexValidator(code='invalid_username', message='Username cannot contain spaces', regex='^\\S+$')]),
        ),
    ]
