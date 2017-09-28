# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parladata', '0007_auto_20160429_1244'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='membership',
            field=models.ForeignKey(related_name='memberships', blank=True, to='parladata.Membership', help_text='The post held by the person in the organization through this membership', null=True),
        ),
    ]
