# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import tinymce.models


class Migration(migrations.Migration):

    dependencies = [
        ('parladata', '0029_auto_20171013_1109'),
    ]

    operations = [
        migrations.RenameField(
            model_name='law',
            old_name='result',
            new_name='status',
        ),
        migrations.AddField(
            model_name='law',
            name='note',
            field=tinymce.models.HTMLField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='law',
            name='procedure',
            field=models.CharField(help_text=b'Procedure of law', max_length=255, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='law',
            name='procedure_phase',
            field=models.CharField(help_text=b'Procedure phase of law', max_length=255, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='law',
            name='proposer_text',
            field=models.CharField(help_text=b'Proposer of law', max_length=255, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='law',
            name='type_of_law',
            field=models.CharField(help_text=b'Type of law', max_length=255, null=True, blank=True),
        ),
    ]
