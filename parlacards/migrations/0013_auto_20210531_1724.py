# Generated by Django 3.2 on 2021-05-31 17:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('parladata', '0029_auto_20210524_1152'),
        ('parlacards', '0012_merge_20210531_1707'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='PersonMonthlyPresenceOnVote',
            new_name='PersonMonthlyVoteAttendance',
        ),
        migrations.RenameModel(
            old_name='PersonPresenceOnVotes',
            new_name='PersonVoteAttendance',
        ),
    ]
