# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parladata', '0002_auto_20151024_1100'),
    ]

    operations = [
        migrations.AddField(
            model_name='session',
            name='in_review',
            field=models.BooleanField(default=False, help_text=b'Is session in review?'),
        ),
    ]
