# Generated by Django 3.2.12 on 2022-11-22 12:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parladata', '0065_task_module_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='email_msg',
            field=models.TextField(default='', help_text='A message sent to the administrator when the task is complete.'),
            preserve_default=False,
        ),
    ]
