# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parladata', '0005_vote_epa'),
    ]

    operations = [
        migrations.AddField(
            model_name='vote',
            name='gov_url',
            field=models.CharField(help_text=b'gov url for this vote', max_length=515, null=True, blank=True),
        ),
    ]
