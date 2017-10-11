# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone
import model_utils.fields
import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
        ('taggit', '0002_auto_20150616_2121'),
        ('parladata', '0027_auto_20170818_1139'),
    ]

    operations = [
        migrations.CreateModel(
            name='Law',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='creation time', editable=False)),
                ('updated_at', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='last modification time', editable=False)),
                ('uid', models.CharField(help_text=b'law uid from DZ page', max_length=64, null=True, blank=True)),
                ('text', models.TextField(help_text=b'The text of the law', null=True, blank=True)),
                ('epa', models.CharField(help_text=b'EPA number', max_length=255, null=True, blank=True)),
                ('mdt', models.CharField(help_text=b'Working body', max_length=255, null=True, blank=True)),
                ('result', models.CharField(help_text=b'result of law', max_length=255, null=True, blank=True)),
                ('session', models.ForeignKey(blank=True, to='parladata.Session', help_text=b'The legislative session in which the law was proposed', null=True)),
                ('tags', taggit.managers.TaggableManager(to='taggit.Tag', through='taggit.TaggedItem', help_text='A comma-separated list of tags.', verbose_name='Tags')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='motion',
            name='title',
            field=models.TextField(help_text=b'Motion classification', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='vote',
            name='motion',
            field=models.ForeignKey(related_name='vote', blank=True, to='parladata.Motion', help_text=b'The motion for which the vote took place', null=True),
        ),
    ]
