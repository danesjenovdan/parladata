# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import parladata.models


class Migration(migrations.Migration):

    dependencies = [
        ('parladata', '0031_auto_20171027_1234'),
    ]

    operations = [
        migrations.AddField(
            model_name='law',
            name='classification',
            field=models.CharField(help_text=b'Type of law', max_length=255, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='law',
            name='date',
            field=parladata.models.PopoloDateTimeField(help_text=b'Date of the question.', null=True, blank=True),
        ),
        migrations.AddField(
            model_name='law',
            name='procedure_ended',
            field=models.BooleanField(default=False, help_text=b'Procedure phase of law', max_length=255),
        ),
        migrations.AddField(
            model_name='law',
            name='result',
            field=models.CharField(help_text=b'result of law', max_length=255, null=True, blank=True),
        ),
    ]
