# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parladata', '0028_auto_20170930_1309'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='law',
            name='date',
        ),
        migrations.RemoveField(
            model_name='law',
            name='gov_id',
        ),
        migrations.RemoveField(
            model_name='law',
            name='gov_url',
        ),
        migrations.RemoveField(
            model_name='law',
            name='mdt',
        ),
        migrations.RemoveField(
            model_name='law',
            name='motion',
        ),
        migrations.RemoveField(
            model_name='law',
            name='organization',
        ),
        migrations.RemoveField(
            model_name='law',
            name='phase',
        ),
        migrations.RemoveField(
            model_name='law',
            name='recap',
        ),
        migrations.RemoveField(
            model_name='law',
            name='result',
        ),
        migrations.RemoveField(
            model_name='law',
            name='type_procedure',
        ),
    ]
