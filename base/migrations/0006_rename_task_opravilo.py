# Generated by Django 4.1 on 2022-08-30 20:51

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('base', '0005_rename_user_task_uporabnik'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Task',
            new_name='Opravilo',
        ),
    ]
