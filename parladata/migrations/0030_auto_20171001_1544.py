# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parladata', '0029_auto_20170930_1852'),
    ]

    operations = [
        migrations.AddField(
            model_name='law',
            name='mdt',
            field=models.CharField(help_text=b'Working body', max_length=255, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='law',
            name='result',
            field=models.CharField(help_text=b'result of law', max_length=255, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='motion',
            name='title',
            field=models.TextField(help_text=b'Motion classification', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='law',
            name='session',
            field=models.ForeignKey(blank=True, to='parladata.Session', help_text=b'The legislative session in which the law was proposed', null=True),
        ),
        migrations.AlterField(
            model_name='law',
            name='text',
            field=models.TextField(help_text=b'The text of the law', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='law',
            name='uid',
            field=models.CharField(help_text=b'law uid from DZ page', max_length=64, null=True, blank=True),
        ),
    ]
