# Generated by Django 3.1.2 on 2021-04-09 13:48

from django.db import migrations, models
import parladata.models


class Migration(migrations.Migration):

    dependencies = [
        ('parladata', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='date_of_answer',
            field=models.DateTimeField(blank=True, help_text='Date of answer the question.', null=True),
        ),
    ]
