# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parladata', '0025_auto_20170709_1125'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='author_org',
            field=models.ForeignKey(related_name='asked', blank=True, to='parladata.Organization', help_text=b'The organization of person (MP) who asked the question.', null=True),
        ),
    ]
