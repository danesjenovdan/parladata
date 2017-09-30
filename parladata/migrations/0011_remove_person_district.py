# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parladata', '0010_person_districts'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='person',
            name='district',
        ),
    ]
