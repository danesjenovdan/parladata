# Generated by Django 3.2.7 on 2021-10-25 16:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('parladata', '0045_auto_20210913_1845'),
    ]

    operations = [
        migrations.CreateModel(
            name='EducationLevel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True, db_index=True)),
                ('text', models.TextField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.RemoveField(
            model_name='personeducationlevel',
            name='value',
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
        migrations.AddField(
            model_name='personeducationlevel',
            name='education_level',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='parladata.educationlevel', verbose_name='Education level'),
        ),
    ]
