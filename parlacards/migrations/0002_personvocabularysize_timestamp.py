# Generated by Django 3.2 on 2021-05-19 21:07

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parlacards', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='personvocabularysize',
            name='timestamp',
            field=models.DateTimeField(default=datetime.datetime(2021, 5, 19, 21, 7, 34, 60103)),
            preserve_default=False,
        ),
    ]
