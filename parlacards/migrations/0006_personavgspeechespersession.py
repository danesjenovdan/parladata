# Generated by Django 3.2 on 2021-05-24 07:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("parladata", "0028_auto_20210523_1728"),
        ("parlacards", "0005_votingdistance"),
    ]

    operations = [
        migrations.CreateModel(
            name="PersonAvgSpeechesPerSession",
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
                    "person",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="parladata.person",
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
