# Generated by Django 3.1.2 on 2021-04-23 13:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('parladata', '0002_question_date_of_answer'),
    ]

    operations = [
        migrations.RenameField(
            model_name='person',
            old_name='birth_date',
            new_name='date_of_birth',
        ),
        migrations.RenameField(
            model_name='person',
            old_name='death_date',
            new_name='date_of_death',
        ),
        migrations.RemoveField(
            model_name='organization',
            name='_acronym',
        ),
        migrations.RemoveField(
            model_name='organization',
            name='_name',
        ),
        migrations.RemoveField(
            model_name='organization',
            name='is_coalition',
        ),
        migrations.RemoveField(
            model_name='organization',
            name='name_parser',
        ),
        migrations.RemoveField(
            model_name='organization',
            name='voters',
        ),
        migrations.RemoveField(
            model_name='person',
            name='additional_name',
        ),
        migrations.RemoveField(
            model_name='person',
            name='biography',
        ),
        migrations.RemoveField(
            model_name='person',
            name='classification',
        ),
        migrations.RemoveField(
            model_name='person',
            name='family_name',
        ),
        migrations.RemoveField(
            model_name='person',
            name='gender',
        ),
        migrations.RemoveField(
            model_name='person',
            name='given_name',
        ),
        migrations.RemoveField(
            model_name='person',
            name='gov_id',
        ),
        migrations.RemoveField(
            model_name='person',
            name='gov_picture_url',
        ),
        migrations.RemoveField(
            model_name='person',
            name='gov_url',
        ),
        migrations.RemoveField(
            model_name='person',
            name='mandates',
        ),
        migrations.RemoveField(
            model_name='person',
            name='name_parser',
        ),
        migrations.RemoveField(
            model_name='person',
            name='patronymic_name',
        ),
        migrations.RemoveField(
            model_name='person',
            name='points',
        ),
        migrations.RemoveField(
            model_name='person',
            name='sort_name',
        ),
        migrations.RemoveField(
            model_name='person',
            name='summary',
        ),
        migrations.RemoveField(
            model_name='person',
            name='voters',
        ),
        migrations.AddField(
            model_name='organizationname',
            name='parser_names',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='person',
            name='number_of_mandates',
            field=models.IntegerField(blank=True, help_text="Person's number of mandates, including the current one", null=True, verbose_name='number of mandates'),
        ),
        migrations.AddField(
            model_name='person',
            name='number_of_points',
            field=models.IntegerField(blank=True, default=None, help_text='number of points cast for this person (in a point-based voting system)', null=True, verbose_name='number of points awarded'),
        ),
        migrations.AddField(
            model_name='person',
            name='number_of_voters',
            field=models.IntegerField(blank=True, help_text='number of votes cast for this person in their district(s)', null=True, verbose_name='number of voters'),
        ),
        migrations.AddField(
            model_name='person',
            name='parser_names',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='person',
            name='preferred_pronoun',
            field=models.CharField(blank=True, help_text='Persons preferred pronoun', max_length=128, null=True, verbose_name='preferred pronoun'),
        ),
        migrations.AlterField(
            model_name='organizationname',
            name='organization',
            field=models.ForeignKey(help_text='The organization that holds this name.', on_delete=django.db.models.deletion.CASCADE, related_name='names', to='parladata.organization'),
        ),
        migrations.AlterField(
            model_name='person',
            name='education',
            field=models.TextField(blank=True, help_text='The person\'s education. Their "topic", like "computer science".', null=True, verbose_name='education'),
        ),
        migrations.AlterField(
            model_name='person',
            name='education_level',
            field=models.TextField(blank=True, help_text="The person's education level (what they would use to determine their pay in the public sector).", null=True, verbose_name='education level'),
        ),
        migrations.AlterField(
            model_name='person',
            name='email',
            field=models.EmailField(blank=True, help_text='Official (office) email', max_length=254, null=True, verbose_name='email'),
        ),
        migrations.AlterField(
            model_name='person',
            name='image',
            field=models.ImageField(blank=True, help_text='A image of a head shot', null=True, upload_to='', verbose_name='image (url)'),
        ),
    ]
