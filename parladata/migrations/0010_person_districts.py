# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from parladata.models import Person


class Migration(migrations.Migration):

    dependencies = [
        ('parladata', '0009_remove_membership_post'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='districts',
            field=models.ManyToManyField(help_text=b'District', related_name='candidates', null=True, to='parladata.Area', blank=True),
        ),
    ]
