# Generated by Django 4.1 on 2022-08-30 11:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0002_alter_task_options_rename_title_task_naslov_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='task',
            options={'ordering': ['created']},
        ),
        migrations.RenameField(
            model_name='task',
            old_name='opravljeno',
            new_name='complete',
        ),
        migrations.RenameField(
            model_name='task',
            old_name='ustvarjeno',
            new_name='created',
        ),
        migrations.RenameField(
            model_name='task',
            old_name='opis',
            new_name='description',
        ),
        migrations.RenameField(
            model_name='task',
            old_name='naslov',
            new_name='title',
        ),
        migrations.RenameField(
            model_name='task',
            old_name='uporabnik',
            new_name='user',
        ),
    ]
