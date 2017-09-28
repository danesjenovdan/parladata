# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone
import model_utils.fields
import parladata.models


class Migration(migrations.Migration):

    dependencies = [
        ('parladata', '0018_auto_20170217_1724'),
    ]

    operations = [
        migrations.AddField(
            model_name='motion',
            name='uuid',
            field=models.UUIDField(help_text=b'motions uuid from DZ page', null=True, blank=True),
        ),
    ]
