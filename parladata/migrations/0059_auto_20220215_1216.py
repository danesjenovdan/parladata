# Generated by Django 3.2.10 on 2022-02-15 12:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parladata', '0058_alter_motion_title'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='medium',
            options={'ordering': ['order']},
        ),
        migrations.AddField(
            model_name='medium',
            name='order',
            field=models.PositiveIntegerField(default=1),
        ),
    ]
