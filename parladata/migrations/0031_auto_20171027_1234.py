# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parladata', '0030_auto_20171027_1210'),
    ]

    operations = [
        migrations.AddField(
            model_name='law',
            name='mdt_fk',
            field=models.ForeignKey(related_name='laws', blank=True, to='parladata.Organization', max_length=255, help_text=b'Working body obj', null=True),
        ),
        migrations.AlterField(
            model_name='law',
            name='mdt',
            field=models.CharField(help_text=b'Working body text', max_length=255, null=True, blank=True),
        ),
    ]
