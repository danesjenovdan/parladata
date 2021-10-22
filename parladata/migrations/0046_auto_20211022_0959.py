# Generated by Django 3.2.7 on 2021-10-22 09:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('parladata', '0045_auto_20210913_1845'),
    ]

    operations = [
        migrations.CreateModel(
            name='LegislationStatus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True, db_index=True)),
                ('name', models.TextField(blank=True, help_text='Status of legisaltion', null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Procedure',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True, db_index=True)),
                ('type', models.TextField(blank=True, help_text='Name of procedure type', null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AlterField(
            model_name='organizationmembership',
            name='organization',
            field=models.ForeignKey(help_text='The organization that the member belongs to.', on_delete=django.db.models.deletion.CASCADE, related_name='organizationmemberships_children', to='parladata.organization'),
        ),
        migrations.AlterField(
            model_name='personmembership',
            name='organization',
            field=models.ForeignKey(help_text='The organization that the member belongs to.', on_delete=django.db.models.deletion.CASCADE, related_name='personmemberships_children', to='parladata.organization'),
        ),
        migrations.AlterField(
            model_name='personmembership',
            name='role',
            field=models.TextField(choices=[('member', 'member'), ('voter', 'voter'), ('president', 'president'), ('deputy', 'deputy'), ('leader', 'leader')], default='member', help_text='The role that the person fulfills in the organization', verbose_name='role'),
        ),
        migrations.CreateModel(
            name='ProcedurePhase',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True, db_index=True)),
                ('name', models.TextField(blank=True, help_text='Name of procedure type', null=True)),
                ('procedure_phase', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='parladata.procedure')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='LegislationConsideration',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True, db_index=True)),
                ('timestamp', models.DateTimeField(blank=True, help_text='Date of the law.', null=True)),
                ('legislation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='parladata.law')),
                ('organization', models.ForeignKey(blank=True, help_text='Organization in which consideration happened', null=True, on_delete=django.db.models.deletion.CASCADE, to='parladata.organization')),
                ('procedure_phase', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='parladata.procedurephase')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='law',
            name='considerations',
            field=models.ManyToManyField(blank=True, help_text='Consideration of legislation', through='parladata.LegislationConsideration', to='parladata.ProcedurePhase'),
        ),
        migrations.AddField(
            model_name='link',
            name='legislation_consideration',
            field=models.ForeignKey(blank=True, help_text='The legislation consideration this link belongs to.', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='links', to='parladata.legislationconsideration'),
        ),
        migrations.AlterField(
            model_name='law',
            name='status',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='parladata.legislationstatus'),
        ),
    ]
