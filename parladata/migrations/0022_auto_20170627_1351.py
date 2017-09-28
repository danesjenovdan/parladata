# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone
import model_utils.fields
import parladata.models


class Migration(migrations.Migration):

    dependencies = [
        ('parladata', '0021_auto_20170512_1049'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='recipient_post',
            field=models.ManyToManyField(help_text=b"Recipient person's post).", related_name='questions', to='parladata.Post', blank=True),
        ),
        migrations.AlterField(
            model_name='area',
            name='calssification',
            field=models.CharField(help_text=b'Area classification (Unit/Region)', max_length=128, null=True, verbose_name='classification', blank=True),
        ),
        migrations.AlterField(
            model_name='link',
            name='motion',
            field=models.ForeignKey(related_name='links', blank=True, to='parladata.Motion', help_text=b'The motion of this link.', null=True),
        ),
        migrations.AlterField(
            model_name='link',
            name='organization',
            field=models.ForeignKey(related_name='links', blank=True, to='parladata.Organization', help_text=b'The organization of this link.', null=True),
        ),
        migrations.AlterField(
            model_name='person',
            name='active',
            field=models.BooleanField(default=True, help_text=b'a generic active or not toggle', verbose_name='active'),
        ),
        migrations.AlterField(
            model_name='person',
            name='classification',
            field=models.CharField(help_text=b'Classification for sorting purposes.', max_length=128, null=True, verbose_name='classification', blank=True),
        ),
        migrations.AlterField(
            model_name='person',
            name='districts',
            field=models.ManyToManyField(help_text=b'District of person', related_name='candidates', null=True, to='parladata.Area', blank=True),
        ),
        migrations.AlterField(
            model_name='person',
            name='gov_id',
            field=models.CharField(help_text=b'gov website id for the scraper', max_length=255, null=True, verbose_name='gov_id', blank=True),
        ),
        migrations.AlterField(
            model_name='person',
            name='voters',
            field=models.IntegerField(help_text=b'number of votes cast for this person in their district', null=True, verbose_name='voters', blank=True),
        ),
        migrations.AlterField(
            model_name='question',
            name='json_data',
            field=models.TextField(help_text='Debug data', null=True, verbose_name='json', blank=True),
        ),
        migrations.AlterField(
            model_name='question',
            name='title',
            field=models.TextField(help_text=b'Title name as written on dz-rs.si', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='session',
            name='organization',
            field=models.ForeignKey(related_name='session', blank=True, to='parladata.Organization', help_text=b'The organization in session', null=True),
        ),
    ]
