# Generated by Django 3.2.12 on 2022-09-08 18:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('parladata', '0063_alter_motion_law'),
    ]

    operations = [
        migrations.AddField(
            model_name='law',
            name='mandate',
            field=models.ForeignKey(blank=True, help_text='The mandate of this law.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='legislation', to='parladata.mandate'),
        ),
        migrations.AlterField(
            model_name='personmembership',
            name='role',
            field=models.TextField(choices=[('member', 'member'), ('deputy member', 'deputy member'), ('voter', 'voter'), ('president', 'president'), ('deputy', 'deputy'), ('leader', 'leader')], default='member', help_text='The role that the person fulfills in the organization', verbose_name='role'),
        ),
    ]
