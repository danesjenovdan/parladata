# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone
import model_utils.fields
import parladata.models


class Migration(migrations.Migration):

    dependencies = [
        ('parladata', '0022_auto_20170627_1351'),
    ]

    operations = [
        migrations.CreateModel(
            name='session_deleted',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='creation time', editable=False)),
                ('updated_at', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='last modification time', editable=False)),
                ('mandate_id', models.IntegerField(null=True, blank=True)),
                ('name', models.CharField(help_text=b'Session name', max_length=255, null=True, blank=True)),
                ('gov_id', models.CharField(help_text=b'Gov website ID.', max_length=255, null=True, blank=True)),
                ('start_time', parladata.models.PopoloDateTimeField(help_text=b'Start time', null=True, blank=True)),
                ('end_time', parladata.models.PopoloDateTimeField(help_text=b'End time', null=True, blank=True)),
                ('organization_id', models.IntegerField(null=True, blank=True)),
                ('classification', models.CharField(help_text=b'Session classification', max_length=128, null=True, blank=True)),
                ('in_review', models.BooleanField(default=False, help_text=b'Is session in review?')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='tmp_votelinks',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='creation time', editable=False)),
                ('updated_at', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='last modification time', editable=False)),
                ('session_id', models.CharField(max_length=255, null=True, blank=True)),
                ('gov_id', models.CharField(max_length=255, null=True, blank=True)),
                ('votedoc_url', models.CharField(max_length=255, null=True, blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
