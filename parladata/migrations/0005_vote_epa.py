# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parladata', '0004_vote_tags'),
    ]

    operations = [
        migrations.AddField(
            model_name='vote',
            name='epa',
            field=models.CharField(help_text=b'EPA number', max_length=255, null=True, blank=True),
        ),
    ]
