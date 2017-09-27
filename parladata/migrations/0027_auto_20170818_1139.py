# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parladata', '0026_question_author_org'),
    ]

    operations = [
        migrations.CreateModel(
            name='PersonEducation',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('parladata.person',),
        ),
        migrations.AddField(
            model_name='person',
            name='education_level',
            field=models.TextField(help_text="The person's education level", null=True, verbose_name='education level', blank=True),
        ),
    ]
