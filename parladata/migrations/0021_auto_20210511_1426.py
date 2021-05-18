# Generated by Django 3.2 on 2021-05-11 14:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('parladata', '0020_auto_20210511_1316'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='law',
            name='classification',
        ),
        migrations.RemoveField(
            model_name='law',
            name='procedure',
        ),
        migrations.RemoveField(
            model_name='law',
            name='procedure_ended',
        ),
        migrations.RemoveField(
            model_name='law',
            name='procedure_phase',
        ),
        migrations.RemoveField(
            model_name='law',
            name='result',
        ),
        migrations.RemoveField(
            model_name='law',
            name='type_of_law',
        ),
        migrations.RemoveField(
            model_name='motion',
            name='debate',
        ),
        migrations.RemoveField(
            model_name='motion',
            name='epa',
        ),
        migrations.RemoveField(
            model_name='motion',
            name='gov_id',
        ),
        migrations.RemoveField(
            model_name='motion',
            name='uid',
        ),
        migrations.RemoveField(
            model_name='speech',
            name='debate',
        ),
        migrations.RemoveField(
            model_name='vote',
            name='end_time',
        ),
        migrations.RemoveField(
            model_name='vote',
            name='start_time',
        ),
        migrations.AddField(
            model_name='law',
            name='law_type',
            field=models.TextField(blank=True, help_text='Type of law', null=True),
        ),
        migrations.AddField(
            model_name='law',
            name='passed',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='law',
            name='procedure_type',
            field=models.TextField(blank=True, help_text='Skrajšani, normalni, hitri postopek...', max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='motion',
            name='law',
            field=models.ForeignKey(blank=True, help_text='Piece of legislation this motion is about', null=True, on_delete=django.db.models.deletion.CASCADE, to='parladata.law'),
        ),
        migrations.AddField(
            model_name='motion',
            name='parser_names',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='vote',
            name='datetime',
            field=models.DateTimeField(blank=True, help_text='Vote time', null=True),
        ),
        migrations.AlterField(
            model_name='law',
            name='status',
            field=models.TextField(blank=True, help_text='result of law', null=True),
        ),
        migrations.DeleteModel(
            name='Debate',
        ),
    ]
