# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parladata', '0006_vote_gov_url'),
    ]

    operations = [
        migrations.RenameField(
            model_name='vote',
            old_name='gov_url',
            new_name='epa_url',
        ),
        migrations.AddField(
            model_name='vote',
            name='document_url',
            field=models.CharField(help_text=b'"document" url for this vote', max_length=515, null=True, blank=True),
        ),
    ]
