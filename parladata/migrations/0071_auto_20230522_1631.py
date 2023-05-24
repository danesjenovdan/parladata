# Generated by Django 3.2.12 on 2023-05-22 16:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parladata', '0070_auto_20230522_1431'),
    ]

    operations = [
        migrations.AddField(
            model_name='publicpersonanswer',
            name='gov_id',
            field=models.TextField(blank=True, help_text='Gov ID or identifier for parser', null=True),
        ),
        migrations.AddField(
            model_name='publicpersonquestion',
            name='gov_id',
            field=models.TextField(blank=True, help_text='Gov ID or identifier for parser', null=True),
        ),
    ]