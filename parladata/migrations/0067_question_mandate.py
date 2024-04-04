# Generated by Django 3.2.12 on 2022-11-23 14:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("parladata", "0066_task_email_msg"),
    ]

    operations = [
        migrations.AddField(
            model_name="question",
            name="mandate",
            field=models.ForeignKey(
                blank=True,
                help_text="The mandate of this question.",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="questions",
                to="parladata.mandate",
            ),
        ),
    ]
