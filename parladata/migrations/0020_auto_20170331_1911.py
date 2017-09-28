# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone
import model_utils.fields
import parladata.models


class Migration(migrations.Migration):

    dependencies = [
        ('parladata', '0019_auto_20170315_1229'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='question',
            name='recipient_organization',
        ),
        migrations.AddField(
            model_name='question',
            name='recipient_organization',
            field=models.ManyToManyField(help_text=b"Recipient organization (if it's an organization).", related_name='questions_org', to='parladata.Organization', blank=True),
        ),
        migrations.RemoveField(
            model_name='question',
            name='recipient_person',
        ),
        migrations.AddField(
            model_name='question',
            name='recipient_person',
            field=models.ManyToManyField(help_text=b"Recipient person (if it's a person).", related_name='questions', to='parladata.Person', blank=True),
        ),
    ]
