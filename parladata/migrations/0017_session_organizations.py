# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parladata', '0016_question_json_data'),
    ]

    operations = [
        migrations.AddField(
            model_name='session',
            name='organizations',
            field=models.ManyToManyField(help_text=b'The organization in session', related_name='sessions', to='parladata.Organization'),
        ),
    ]
