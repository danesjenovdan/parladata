# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone
import model_utils.fields
import parladata.models


class Migration(migrations.Migration):

    dependencies = [
        ('parladata', '0017_session_organizations'),
    ]

    operations = [
        migrations.AddField(
            model_name='motion',
            name='epa',
            field=models.CharField(help_text=b'EPA number', max_length=255, null=True, blank=True),
        ),
    ]
