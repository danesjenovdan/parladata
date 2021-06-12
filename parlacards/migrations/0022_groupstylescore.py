# Generated by Django 3.2.3 on 2021-06-12 19:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('parladata', '0030_speech_lemmatized_content'),
        ('parlacards', '0021_grouptfidf'),
    ]

    operations = [
        migrations.CreateModel(
            name='GroupStyleScore',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True, db_index=True)),
                ('timestamp', models.DateTimeField()),
                ('value', models.FloatField()),
                ('style', models.TextField()),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='groupstylescore_related', to='parladata.organization')),
                ('playing_field', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='parladata.organization')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
