# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parladata', '0015_auto_20170106_1553'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='json_data',
            field=models.TextField(help_text='debug data', null=True, verbose_name='json', blank=True),
        ),
    ]
