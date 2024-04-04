# Generated by Django 3.2.4 on 2021-06-07 09:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("parladata", "0030_speech_lemmatized_content"),
        ("parlacards", "0018_persontfidf"),
    ]

    operations = [
        migrations.CreateModel(
            name="GroupVoteAttendance",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True, db_index=True)),
                ("timestamp", models.DateTimeField()),
                ("value", models.FloatField()),
                (
                    "group",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="groupvoteattendance_related",
                        to="parladata.organization",
                    ),
                ),
                (
                    "playing_field",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="parladata.organization",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
