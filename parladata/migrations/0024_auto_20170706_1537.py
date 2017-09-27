# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parladata', '0023_session_deleted_tmp_votelinks'),
    ]

    operations = [
        migrations.AddField(
            model_name='organization',
            name='name_parser',
            field=models.CharField(help_text=b'Name for parser.', max_length=500, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='person',
            name='districts',
            field=models.ManyToManyField(help_text=b'District of person', related_name='candidates', to='parladata.Area', blank=True),
        ),
    ]
