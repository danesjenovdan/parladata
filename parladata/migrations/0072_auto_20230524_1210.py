# Generated by Django 3.2.12 on 2023-05-24 12:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('parladata', '0071_auto_20230522_1631'),
    ]

    operations = [
        migrations.AlterField(
            model_name='legislationconsideration',
            name='legislation',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='legislationconsiderations', to='parladata.law'),
        ),
        migrations.AlterField(
            model_name='legislationconsideration',
            name='session',
            field=models.ForeignKey(blank=True, help_text='Session at which the legislation was discussed', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='legislationconsiderations', to='parladata.session'),
        ),
    ]
