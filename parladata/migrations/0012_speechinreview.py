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
        ('parladata', '0011_remove_person_district'),
    ]

    operations = [
        migrations.CreateModel(
            name='SpeechInReview',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='creation time', editable=False)),
                ('updated_at', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='last modification time', editable=False)),
                ('content', models.TextField(help_text=b'Words spoken')),
                ('order', models.IntegerField(help_text=b'Order of speech', null=True, blank=True)),
                ('start_time', parladata.models.PopoloDateTimeField(help_text=b'Start time', null=True, blank=True)),
                ('end_time', parladata.models.PopoloDateTimeField(help_text=b'End time', null=True, blank=True)),
                ('party', models.ForeignKey(default=2, to='parladata.Organization', help_text=b'The party of the person making the speech')),
                ('session', models.ForeignKey(blank=True, to='parladata.Session', help_text=b'Speech session', null=True)),
                ('speaker', models.ForeignKey(help_text=b'Person making the speech', to='parladata.Person')),
                ('tags', taggit.managers.TaggableManager(to='taggit.Tag', through='taggit.TaggedItem', help_text='A comma-separated list of tags.', verbose_name='Tags')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
