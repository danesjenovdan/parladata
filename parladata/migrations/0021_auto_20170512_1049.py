# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import model_utils.fields
import parladata.models
import django.utils.timezone
import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
        ('taggit', '0002_auto_20150616_2121'),
        ('parladata', '0020_auto_20170331_1911'),
    ]

    operations = [
        migrations.CreateModel(
            name='Ignore',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='creation time', editable=False)),
                ('updated_at', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='last modification time', editable=False)),
                ('uid', models.CharField(help_text=b'motions uid from DZ page', max_length=64, null=True, blank=True)),
                ('tags', taggit.managers.TaggableManager(to='taggit.Tag', through='taggit.TaggedItem', help_text='A comma-separated list of tags.', verbose_name='Tags')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.RemoveField(
            model_name='motion',
            name='uuid',
        ),
        migrations.AddField(
            model_name='motion',
            name='uid',
            field=models.CharField(help_text=b'motions uid from DZ page', max_length=64, null=True, blank=True),
        ),
    ]
