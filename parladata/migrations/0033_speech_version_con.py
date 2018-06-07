# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parladata', '0032_auto_20171208_1115'),
    ]

    operations = [
        migrations.AddField(
            model_name='speech',
            name='version_con',
            field=models.IntegerField(help_text=b'Order of speech', null=True, blank=True),
        ),
    ]
