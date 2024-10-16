# Generated by Django 3.2 on 2021-06-01 10:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('parladata', '0029_auto_20210524_1152'),
        ('parlacards', '0013_auto_20210531_1724'),
    ]

    operations = [
        migrations.AlterField(
            model_name='groupvocabularysize',
            name='group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='groupvocabularysize_related', to='parladata.organization'),
        ),
        migrations.CreateModel(
            name='GroupMonthlyVoteAttendance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True, db_index=True)),
                ('timestamp', models.DateTimeField()),
                ('value', models.FloatField()),
                ('no_mandate', models.FloatField()),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='groupmonthlyvoteattendance_related', to='parladata.organization')),
                ('playing_field', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='parladata.organization')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
