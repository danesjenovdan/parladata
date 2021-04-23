# Generated by Django 3.1.2 on 2021-04-23 15:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('parladata', '0004_auto_20210423_1538'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='identifier',
            name='organization',
        ),
        migrations.RemoveField(
            model_name='identifier',
            name='person',
        ),
        migrations.RemoveField(
            model_name='ignore',
            name='tags',
        ),
        migrations.RemoveField(
            model_name='othername',
            name='organization',
        ),
        migrations.RemoveField(
            model_name='othername',
            name='person',
        ),
        migrations.DeleteModel(
            name='session_deleted',
        ),
        migrations.DeleteModel(
            name='tmp_votelinks',
        ),
        migrations.DeleteModel(
            name='Identifier',
        ),
        migrations.DeleteModel(
            name='Ignore',
        ),
        migrations.DeleteModel(
            name='OtherName',
        ),
    ]
