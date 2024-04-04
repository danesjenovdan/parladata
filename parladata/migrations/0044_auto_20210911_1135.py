# Generated by Django 3.2.7 on 2021-09-11 11:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("parladata", "0043_auto_20210909_1016"),
    ]

    operations = [
        migrations.AddField(
            model_name="organization",
            name="mandate",
            field=models.ForeignKey(
                blank=True,
                help_text="The mandate of this root organization",
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="organizations",
                to="parladata.mandate",
            ),
        ),
        migrations.AddField(
            model_name="organizationmembership",
            name="mandate",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="parladata.mandate",
                verbose_name="Mandate",
            ),
        ),
        migrations.AddField(
            model_name="personmembership",
            name="mandate",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="parladata.mandate",
                verbose_name="Mandate",
            ),
        ),
    ]
