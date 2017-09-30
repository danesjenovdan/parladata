# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone
import model_utils.fields
import taggit.managers
import parladata.models


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
                ('uid', models.CharField(help_text=b'motions uid from DZ page', max_length=64, null=True, blank=True)),
                ('gov_id', models.CharField(help_text=b'Government website id', max_length=255, null=True, blank=True)),
                ('date', parladata.models.PopoloDateTimeField(help_text=b'The date when the motion was proposed', null=True, blank=True)),
                ('recap', models.TextField(help_text=b'Motion summary', null=True, blank=True)),
                ('text', models.TextField(help_text=b'The text of the motion', null=True, blank=True)),
                ('phase', models.CharField(help_text=b'Motion classification', max_length=128, null=True, blank=True)),
                ('result', models.CharField(help_text=b'Did the motion pass?', max_length=128, null=True, blank=True)),
                ('type_procedure', models.CharField(help_text=b'Did the motion pass?', max_length=128, null=True, blank=True)),
                ('epa', models.CharField(help_text=b'EPA number', max_length=255, null=True, blank=True)),
                ('gov_url', models.ForeignKey(related_name='gov_url', blank=True, to='parladata.Link', help_text=b'URL to gov website profile', null=True)),
                ('mdt', models.ForeignKey(related_name='mdt_org', blank=True, to='parladata.Organization', help_text=b'Working body', null=True)),
                ('motion', models.ForeignKey(blank=True, to='parladata.Motion', help_text=b'The motion for which the vote took place', null=True)),
                ('organization', models.ForeignKey(related_name='low_org', blank=True, to='parladata.Organization', help_text=b'the organization in which the low is proposed', null=True)),
                ('session', models.ForeignKey(blank=True, to='parladata.Session', help_text=b'The legislative session in which the motion was proposed', null=True)),
                ('tags', taggit.managers.TaggableManager(to='taggit.Tag', through='taggit.TaggedItem', help_text='A comma-separated list of tags.', verbose_name='Tags')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AlterField(
            model_name='vote',
            name='motion',
            field=models.ForeignKey(related_name='vote', blank=True, to='parladata.Motion', help_text=b'The motion for which the vote took place', null=True),
        ),
    ]
