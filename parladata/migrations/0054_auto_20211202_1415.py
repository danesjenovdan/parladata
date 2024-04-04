# Generated by Django 3.2.9 on 2021-12-02 14:15

from django.db import migrations, models
import django.db.models.deletion


# added this to clean the current classification values
def clean_legislation_classifications(apps, schema_editor):
    # We get the model from the versioned app registry;
    # if we directly import it, it'll be the wrong version
    Law = apps.get_model("parladata", "Law")
    db_alias = schema_editor.connection.alias
    all_legislation = Law.objects.using(db_alias).all()
    for law in all_legislation:
        law.classification = None

    Law.objects.using(db_alias).bulk_update(all_legislation, ["classification"])


def reverse_legislation_classifications(apps, schema_editor):
    # TODO maybe something smart should happen, but we're probably fine
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("parladata", "0053_auto_20211201_1150"),
    ]

    operations = [
        migrations.CreateModel(
            name="LegislationClassification",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True, db_index=True)),
                (
                    "name",
                    models.TextField(
                        blank=True, help_text="Status of legisaltion", null=True
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.AlterField(
            model_name="motion",
            name="law",
            field=models.ForeignKey(
                blank=True,
                help_text="Piece of legislation this motion is about",
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="motions",
                to="parladata.law",
            ),
        ),
        migrations.RunPython(
            clean_legislation_classifications, reverse_legislation_classifications
        ),
        migrations.AlterField(
            model_name="law",
            name="classification",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="parladata.legislationclassification",
            ),
        ),
    ]
