# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parladata', '0013_speech_in_review_rel'),
    ]

    operations = [
        migrations.AddField(
            model_name='speech',
            name='valid_from',
            field=models.DateTimeField(default=None, help_text='row valid from', null=True, blank=True),
        ),
        migrations.AddField(
            model_name='speech',
            name='valid_to',
            field=models.DateTimeField(default=None, help_text='row valid to', null=True, blank=True),
        ),
    ]
