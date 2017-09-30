# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone
import model_utils.fields
import parladata.models


class Migration(migrations.Migration):

    dependencies = [
        ('parladata', '0024_auto_20170706_1537'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrganizationName',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='creation time', editable=False)),
                ('updated_at', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='last modification time', editable=False)),
                ('name', models.TextField(help_text='A primary name, e.g. a legally recognized name', verbose_name='name')),
                ('acronym', models.CharField(help_text='Organization acronym', max_length=128, null=True, verbose_name='acronym', blank=True)),
                ('start_time', parladata.models.PopoloDateTimeField(help_text=b'Start time', null=True, blank=True)),
                ('end_time', parladata.models.PopoloDateTimeField(help_text=b'End time', null=True, blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.RenameField(
            model_name='organization',
            old_name='acronym',
            new_name='_acronym',
        ),
        migrations.RenameField(
            model_name='organization',
            old_name='name',
            new_name='_name',
        ),
        migrations.AddField(
            model_name='organizationname',
            name='organization',
            field=models.ForeignKey(related_name='names', to='parladata.Organization', help_text='The organization who hold this name.'),
        ),
    ]
