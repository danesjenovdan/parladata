# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone
import model_utils.fields
import parladata.models


class Migration(migrations.Migration):

    dependencies = [
        ('parladata', '0014_auto_20161228_1847'),
    ]

    operations = [
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='creation time', editable=False)),
                ('updated_at', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='last modification time', editable=False)),
                ('date', parladata.models.PopoloDateTimeField(help_text=b'Date of the question.', null=True, blank=True)),
                ('title', models.TextField(help_text=b'Title  name as written on dz-rs.si', null=True, blank=True)),
                ('recipient_text', models.TextField(help_text=b'Recipient name as written on dz-rs.si', null=True, blank=True)),
                ('author', models.ForeignKey(related_name='asked', blank=True, to='parladata.Person', help_text=b'The person (MP) who asked the question.', null=True)),
                ('recipient_organization', models.ForeignKey(related_name='questions_org', blank=True, to='parladata.Organization', help_text=b"Recipient organization (if it's an organization).", null=True)),
                ('recipient_person', models.ForeignKey(related_name='questions', blank=True, to='parladata.Person', help_text=b"Recipient person (if it's a person).", null=True)),
                ('session', models.ForeignKey(blank=True, to='parladata.Session', help_text=b'The session this question belongs to.', null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.RemoveField(
            model_name='speechinreview',
            name='party',
        ),
        migrations.RemoveField(
            model_name='speechinreview',
            name='session',
        ),
        migrations.RemoveField(
            model_name='speechinreview',
            name='speaker',
        ),
        migrations.RemoveField(
            model_name='speechinreview',
            name='tags',
        ),
        migrations.RemoveField(
            model_name='speech',
            name='in_review_rel',
        ),
        migrations.DeleteModel(
            name='SpeechInReview',
        ),
        migrations.AddField(
            model_name='link',
            name='question',
            field=models.ForeignKey(related_name='links', blank=True, to='parladata.Question', help_text=b'The question this link belongs to.', null=True),
        ),
    ]
