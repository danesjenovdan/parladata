# Generated by Django 3.2 on 2021-05-20 16:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("parladata", "0026_rename_datetime_vote_timestamp"),
        ("parlacards", "0004_organizationvocabularysize"),
    ]

    operations = [
        migrations.CreateModel(
            name="VotingDistance",
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
                (
                    "target",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="target",
                        to="parladata.person",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
