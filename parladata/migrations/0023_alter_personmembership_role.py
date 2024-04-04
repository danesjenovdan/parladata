# Generated by Django 3.2 on 2021-05-12 19:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("parladata", "0022_alter_law_passed"),
    ]

    operations = [
        migrations.AlterField(
            model_name="personmembership",
            name="role",
            field=models.TextField(
                default="member",
                help_text="The role that the person fulfills in the organization",
                verbose_name="role",
            ),
        ),
    ]
