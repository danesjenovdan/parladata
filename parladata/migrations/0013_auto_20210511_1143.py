# Generated by Django 3.2 on 2021-05-11 11:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("parladata", "0012_auto_20210511_1130"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="organizationmembership",
            name="parent",
        ),
        migrations.RemoveField(
            model_name="personmembership",
            name="person",
        ),
        migrations.AddField(
            model_name="organizationmembership",
            name="member",
            field=models.ForeignKey(
                blank=True,
                help_text="The organization that is a party to the relationship",
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="organization_memberships",
                to="parladata.organization",
            ),
        ),
        migrations.AddField(
            model_name="personmembership",
            name="member",
            field=models.ForeignKey(
                default=1,
                help_text="The person who is a party to the relationship",
                on_delete=django.db.models.deletion.CASCADE,
                related_name="person_memberships",
                to="parladata.person",
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="organizationmembership",
            name="organization",
            field=models.ForeignKey(
                help_text="The organization that the member belongs to.",
                on_delete=django.db.models.deletion.CASCADE,
                to="parladata.organization",
            ),
        ),
        migrations.AlterField(
            model_name="personmembership",
            name="on_behalf_of",
            field=models.ForeignKey(
                blank=True,
                help_text="The organization on whose behalf the person is a party to the relationship",
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="representatives",
                to="parladata.organization",
            ),
        ),
        migrations.AlterField(
            model_name="personmembership",
            name="organization",
            field=models.ForeignKey(
                help_text="The organization that the member belongs to.",
                on_delete=django.db.models.deletion.CASCADE,
                to="parladata.organization",
            ),
        ),
    ]
