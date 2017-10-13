# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parladata', '0028_auto_20171001_1601'),
    ]

    operations = [
        migrations.AddField(
            model_name='motion',
            name='doc_title',
            field=models.TextField(help_text=b'Title of document', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='motion',
            name='title',
            field=models.TextField(help_text=b'Title motion', null=True, blank=True),
        ),
    ]
