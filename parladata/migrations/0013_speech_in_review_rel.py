# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parladata', '0012_speechinreview'),
    ]

    operations = [
        migrations.AddField(
            model_name='speech',
            name='in_review_rel',
            field=models.ForeignKey(blank=True, to='parladata.SpeechInReview', null=True),
        ),
    ]
