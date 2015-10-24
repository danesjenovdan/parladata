# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import model_utils.fields
import parladata.models
import django.utils.timezone
import taggit.managers
import djgeojson.fields


class Migration(migrations.Migration):

    dependencies = [
        ('taggit', '0002_auto_20150616_2121'),
    ]

    operations = [
        migrations.CreateModel(
            name='Area',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='creation time', editable=False)),
                ('updated_at', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='last modification time', editable=False)),
                ('name', models.CharField(help_text='Area name', max_length=128, verbose_name='name')),
                ('identifier', models.CharField(help_text=b'Area identifier', max_length=128, null=True, verbose_name='identifier', blank=True)),
                ('geometry', djgeojson.fields.PolygonField(help_text=b'Polygon field for area', null=True, blank=True)),
                ('calssification', models.CharField(help_text=b'Area classification (enota/okraj)', max_length=128, null=True, verbose_name='classification', blank=True)),
                ('parent', models.ForeignKey(blank=True, to='parladata.Area', help_text=b'Area parent', null=True)),
                ('tags', taggit.managers.TaggableManager(to='taggit.Tag', through='taggit.TaggedItem', help_text='A comma-separated list of tags.', verbose_name='Tags')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Ballot',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='creation time', editable=False)),
                ('updated_at', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='last modification time', editable=False)),
                ('option', models.CharField(help_text=b'Yes, no, abstain', max_length=128, null=True, blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ContactDetail',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='creation time', editable=False)),
                ('updated_at', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='last modification time', editable=False)),
                ('label', models.CharField(help_text='A human-readable label for the contact detail', max_length=128, null=True, verbose_name='label', blank=True)),
                ('contact_type', models.CharField(help_text="A type of medium, e.g. 'fax' or 'email'", max_length=12, verbose_name='type', choices=[(b'FAX', 'Fax'), (b'PHONE', 'Telephone'), (b'MOBILE', 'Mobile'), (b'EMAIL', 'Email'), (b'MAIL', 'Snail mail'), (b'TWITTER', 'Twitter'), (b'FACEBOOK', 'Facebook'), (b'LINKEDIN', 'LinkedIn')])),
                ('value', models.CharField(help_text='A value, e.g. a phone number or email address', max_length=128, verbose_name='value')),
                ('note', models.CharField(help_text='A note, e.g. for grouping contact details by physical location', max_length=128, null=True, verbose_name='note', blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Count',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='creation time', editable=False)),
                ('updated_at', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='last modification time', editable=False)),
                ('option', models.CharField(help_text=b'Yes, no, abstain', max_length=128)),
                ('count', models.IntegerField(help_text=b'Number of votes')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Identifier',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('identifier', models.CharField(help_text='An issued identifier, e.g. a DUNS number', max_length=128, verbose_name='identifier')),
                ('scheme', models.CharField(help_text='An identifier scheme, e.g. DUNS', max_length=128, null=True, verbose_name='scheme', blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Link',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='creation time', editable=False)),
                ('updated_at', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='last modification time', editable=False)),
                ('url', models.URLField(help_text='A URL', max_length=350, verbose_name='url')),
                ('note', models.CharField(help_text="A note, e.g. 'Wikipedia page'", max_length=256, null=True, verbose_name='note', blank=True)),
                ('name', models.TextField(null=True, blank=True)),
                ('date', models.DateField(null=True, blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Mandate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.TextField(null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Membership',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='creation time', editable=False)),
                ('updated_at', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='last modification time', editable=False)),
                ('label', models.CharField(help_text='A label describing the membership', max_length=128, null=True, verbose_name='label', blank=True)),
                ('role', models.CharField(help_text='The role that the person fulfills in the organization', max_length=128, null=True, verbose_name='role', blank=True)),
                ('start_time', parladata.models.PopoloDateTimeField(help_text=b'Start time', null=True, blank=True)),
                ('end_time', parladata.models.PopoloDateTimeField(help_text=b'End time', null=True, blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Milestone',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('year', models.IntegerField(help_text='year', null=True, blank=True)),
                ('month', models.IntegerField(help_text='month', null=True, blank=True)),
                ('day', models.IntegerField(help_text='date', null=True, blank=True)),
                ('hour', models.IntegerField(help_text='hour', null=True, blank=True)),
                ('minute', models.IntegerField(help_text='minute', null=True, blank=True)),
                ('second', models.IntegerField(help_text='second', null=True, blank=True)),
                ('kind', models.CharField(help_text=b'type of milestone', max_length=255, null=True, blank=True)),
                ('start_or_end', models.IntegerField(help_text=b'1 for start, -1 for end', null=True, blank=True)),
                ('mandate', models.ForeignKey(blank=True, to='parladata.Mandate', help_text=b'The mandate of this milestone.', null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Motion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='creation time', editable=False)),
                ('updated_at', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='last modification time', editable=False)),
                ('gov_id', models.CharField(help_text=b'Government website id', max_length=255, null=True, blank=True)),
                ('date', parladata.models.PopoloDateTimeField(help_text=b'The date when the motion was proposed', null=True, blank=True)),
                ('recap', models.TextField(help_text=b'Motion summary', null=True, blank=True)),
                ('text', models.TextField(help_text=b'The text of the motion', null=True, blank=True)),
                ('classification', models.CharField(help_text=b'Motion classification', max_length=128, null=True, blank=True)),
                ('requirement', models.CharField(help_text=b'The requirement for the motion to pass', max_length=128, null=True, blank=True)),
                ('result', models.CharField(help_text=b'Did the motion pass?', max_length=128, null=True, blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Organization',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='creation time', editable=False)),
                ('updated_at', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='last modification time', editable=False)),
                ('name', models.CharField(help_text='A primary name, e.g. a legally recognized name', max_length=128, verbose_name='name')),
                ('acronym', models.CharField(help_text='Organization acronym', max_length=128, null=True, verbose_name='acronym', blank=True)),
                ('gov_id', models.TextField(help_text='Gov website ID', null=True, verbose_name='Gov website ID', blank=True)),
                ('classification', models.CharField(help_text='An organization category, e.g. committee', max_length=128, null=True, verbose_name='classification', blank=True)),
                ('dissolution_date', parladata.models.PopoloDateTimeField(help_text='A date of dissolution', null=True, blank=True)),
                ('founding_date', parladata.models.PopoloDateTimeField(help_text='A date of founding', null=True, blank=True)),
                ('description', models.TextField(help_text=b'Organization description', null=True, blank=True)),
                ('is_coalition', models.IntegerField(help_text=b'1 if coalition, -1 if not, 0 if it does not apply', null=True, blank=True)),
                ('parent', models.ForeignKey(related_name='children', blank=True, to='parladata.Organization', help_text='The organization that contains this organization', null=True)),
                ('tags', taggit.managers.TaggableManager(to='taggit.Tag', through='taggit.TaggedItem', help_text='A comma-separated list of tags.', verbose_name='Tags')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='OtherName',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text='An alternate or former name', max_length=128, verbose_name='name')),
                ('note', models.CharField(help_text="A note, e.g. 'Birth name'", max_length=256, null=True, verbose_name='note', blank=True)),
                ('organization', models.ForeignKey(blank=True, to='parladata.Organization', help_text=b'The organization this name belongs to', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='creation time', editable=False)),
                ('updated_at', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='last modification time', editable=False)),
                ('name', models.CharField(help_text="A person's preferred full name", max_length=128, verbose_name='name')),
                ('name_parser', models.CharField(help_text=b'Name for parser.', max_length=500, null=True, blank=True)),
                ('classification', models.CharField(help_text=b'Classification for sorting purposes.', max_length=128, null=True, blank=True)),
                ('family_name', models.CharField(help_text='One or more family names', max_length=128, null=True, verbose_name='family name', blank=True)),
                ('given_name', models.CharField(help_text='One or more primary given names', max_length=128, null=True, verbose_name='given name', blank=True)),
                ('additional_name', models.CharField(help_text='One or more secondary given names', max_length=128, null=True, verbose_name='additional name', blank=True)),
                ('honorific_prefix', models.CharField(help_text="One or more honorifics preceding a person's name", max_length=128, null=True, verbose_name='honorific prefix', blank=True)),
                ('honorific_suffix', models.CharField(help_text="One or more honorifics following a person's name", max_length=128, null=True, verbose_name='honorific suffix', blank=True)),
                ('patronymic_name', models.CharField(help_text='One or more patronymic names', max_length=128, null=True, verbose_name='patronymic name', blank=True)),
                ('sort_name', models.CharField(help_text='A name to use in an lexicographically ordered list', max_length=128, null=True, verbose_name='sort name', blank=True)),
                ('previous_occupation', models.TextField(help_text="The person's previous occupation", null=True, verbose_name='previous occupation', blank=True)),
                ('education', models.TextField(help_text="The person's education", null=True, verbose_name='education', blank=True)),
                ('mandates', models.IntegerField(help_text="Person's number of mandates, including the current one", null=True, verbose_name='mandates', blank=True)),
                ('email', models.EmailField(help_text='A preferred email address', max_length=254, null=True, verbose_name='email', blank=True)),
                ('gender', models.CharField(help_text='A gender', max_length=128, null=True, verbose_name='gender', blank=True)),
                ('birth_date', parladata.models.PopoloDateTimeField(help_text='A date of birth', null=True, verbose_name='date of birth', blank=True)),
                ('death_date', parladata.models.PopoloDateTimeField(help_text='A date of death', null=True, verbose_name='date of death', blank=True)),
                ('summary', models.CharField(help_text="A one-line account of a person's life", max_length=512, null=True, verbose_name='summary', blank=True)),
                ('biography', models.TextField(help_text="An extended account of a person's life", null=True, verbose_name='biography', blank=True)),
                ('image', models.URLField(help_text='A URL of a head shot', null=True, verbose_name='image', blank=True)),
                ('gov_id', models.CharField(help_text=b'gov website id for the scraper', max_length=255, null=True, blank=True)),
                ('gov_picture_url', models.URLField(help_text='URL to gov website pic', null=True, verbose_name='gov image url', blank=True)),
                ('voters', models.IntegerField(help_text=b'number of votes cast for this person in their district', null=True, blank=True)),
                ('active', models.BooleanField(default=True, help_text=b'a generic active or not toggle')),
                ('district', models.ForeignKey(blank=True, to='parladata.Area', help_text=b'District', null=True)),
                ('gov_url', models.ForeignKey(related_name='gov_link', blank=True, to='parladata.Link', help_text=b'URL to gov website profile', null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='creation time', editable=False)),
                ('updated_at', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='last modification time', editable=False)),
                ('label', models.CharField(help_text='A label describing the post', max_length=128, null=True, verbose_name='label', blank=True)),
                ('role', models.CharField(help_text='The function that the holder of the post fulfills', max_length=128, null=True, verbose_name='role', blank=True)),
                ('start_time', parladata.models.PopoloDateTimeField(help_text=b'Start time', null=True, blank=True)),
                ('end_time', parladata.models.PopoloDateTimeField(help_text=b'End time', null=True, blank=True)),
                ('organization', models.ForeignKey(related_name='posts', blank=True, to='parladata.Organization', help_text='The organization in which the post is held', null=True)),
                ('tags', taggit.managers.TaggableManager(to='taggit.Tag', through='taggit.TaggedItem', help_text='A comma-separated list of tags.', verbose_name='Tags')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Session',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='creation time', editable=False)),
                ('updated_at', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='last modification time', editable=False)),
                ('name', models.CharField(help_text=b'Session name', max_length=255, null=True, blank=True)),
                ('gov_id', models.CharField(help_text=b'Gov website ID.', max_length=255, null=True, blank=True)),
                ('start_time', parladata.models.PopoloDateTimeField(help_text=b'Start time', null=True, blank=True)),
                ('end_time', parladata.models.PopoloDateTimeField(help_text=b'End time', null=True, blank=True)),
                ('classification', models.CharField(help_text=b'Session classification', max_length=128, null=True, blank=True)),
                ('mandate', models.ForeignKey(blank=True, to='parladata.Mandate', help_text=b'The mandate of this milestone.', null=True)),
                ('organization', models.ForeignKey(blank=True, to='parladata.Organization', help_text=b'The organization in session', null=True)),
                ('tags', taggit.managers.TaggableManager(to='taggit.Tag', through='taggit.TaggedItem', help_text='A comma-separated list of tags.', verbose_name='Tags')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Source',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='creation time', editable=False)),
                ('updated_at', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='last modification time', editable=False)),
                ('url', models.URLField(help_text='A URL', verbose_name='url')),
                ('note', models.CharField(help_text="A note, e.g. 'Parliament website'", max_length=256, null=True, verbose_name='note', blank=True)),
                ('contact_detail', models.ForeignKey(blank=True, to='parladata.ContactDetail', help_text=b'The person of this source.', null=True)),
                ('membership', models.ForeignKey(blank=True, to='parladata.Membership', help_text=b'The membership of this source.', null=True)),
                ('organization', models.ForeignKey(blank=True, to='parladata.Organization', help_text=b'The organization of this source.', null=True)),
                ('person', models.ForeignKey(blank=True, to='parladata.Person', help_text=b'The person of this source.', null=True)),
                ('post', models.ForeignKey(blank=True, to='parladata.Post', help_text=b'The post of this source.', null=True)),
                ('tags', taggit.managers.TaggableManager(to='taggit.Tag', through='taggit.TaggedItem', help_text='A comma-separated list of tags.', verbose_name='Tags')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Speech',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='creation time', editable=False)),
                ('updated_at', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='last modification time', editable=False)),
                ('content', models.TextField(help_text=b'Words spoken')),
                ('order', models.IntegerField(help_text=b'Order of speech', null=True, blank=True)),
                ('start_time', parladata.models.PopoloDateTimeField(help_text=b'Start time', null=True, blank=True)),
                ('end_time', parladata.models.PopoloDateTimeField(help_text=b'End time', null=True, blank=True)),
                ('party', models.ForeignKey(default=2, to='parladata.Organization', help_text=b'The party of the person making the speech')),
                ('session', models.ForeignKey(blank=True, to='parladata.Session', help_text=b'Speech session', null=True)),
                ('speaker', models.ForeignKey(help_text=b'Person making the speech', to='parladata.Person')),
                ('tags', taggit.managers.TaggableManager(to='taggit.Tag', through='taggit.TaggedItem', help_text='A comma-separated list of tags.', verbose_name='Tags')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Vote',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='creation time', editable=False)),
                ('updated_at', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='last modification time', editable=False)),
                ('name', models.CharField(help_text=b'Vote name/identifier', max_length=1000, null=True, blank=True)),
                ('start_time', parladata.models.PopoloDateTimeField(help_text=b'Start time', null=True, blank=True)),
                ('end_time', parladata.models.PopoloDateTimeField(help_text=b'End time', null=True, blank=True)),
                ('result', models.CharField(help_text=b'The result of the vote', max_length=255, null=True, blank=True)),
                ('motion', models.ForeignKey(blank=True, to='parladata.Motion', help_text=b'The motion for which the vote took place', null=True)),
                ('organization', models.ForeignKey(blank=True, to='parladata.Organization', help_text=b'The organization whose members are voting', null=True)),
                ('session', models.ForeignKey(blank=True, to='parladata.Session', help_text=b'The legislative session in which the vote event occurs', null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='othername',
            name='person',
            field=models.ForeignKey(blank=True, to='parladata.Person', help_text=b'The person this name belongs to', null=True),
        ),
        migrations.AddField(
            model_name='motion',
            name='organization',
            field=models.ForeignKey(blank=True, to='parladata.Organization', help_text=b'the organization in which the motion is proposed', null=True),
        ),
        migrations.AddField(
            model_name='motion',
            name='party',
            field=models.ForeignKey(related_name='motion_party', default=2, to='parladata.Organization', help_text=b'The party of the person who proposed the motion.'),
        ),
        migrations.AddField(
            model_name='motion',
            name='person',
            field=models.ForeignKey(blank=True, to='parladata.Person', help_text=b'The person who proposed the motion', null=True),
        ),
        migrations.AddField(
            model_name='motion',
            name='session',
            field=models.ForeignKey(blank=True, to='parladata.Session', help_text=b'The legislative session in which the motion was proposed', null=True),
        ),
        migrations.AddField(
            model_name='motion',
            name='tags',
            field=taggit.managers.TaggableManager(to='taggit.Tag', through='taggit.TaggedItem', help_text='A comma-separated list of tags.', verbose_name='Tags'),
        ),
        migrations.AddField(
            model_name='milestone',
            name='organization',
            field=models.ForeignKey(blank=True, to='parladata.Organization', help_text=b'The organization of this milestone.', null=True),
        ),
        migrations.AddField(
            model_name='milestone',
            name='person',
            field=models.ForeignKey(blank=True, to='parladata.Person', help_text=b'The person of this milestone.', null=True),
        ),
        migrations.AddField(
            model_name='milestone',
            name='session',
            field=models.ForeignKey(blank=True, to='parladata.Session', help_text=b'The session of this milestone.', null=True),
        ),
        migrations.AddField(
            model_name='milestone',
            name='speech',
            field=models.ForeignKey(blank=True, to='parladata.Speech', help_text=b'The speech of this milestone.', null=True),
        ),
        migrations.AddField(
            model_name='milestone',
            name='tags',
            field=taggit.managers.TaggableManager(to='taggit.Tag', through='taggit.TaggedItem', help_text='A comma-separated list of tags.', verbose_name='Tags'),
        ),
        migrations.AddField(
            model_name='membership',
            name='on_behalf_of',
            field=models.ForeignKey(related_name='memberships_on_behalf_of', blank=True, to='parladata.Organization', help_text='The organization on whose behalf the person is a party to the relationship', null=True),
        ),
        migrations.AddField(
            model_name='membership',
            name='organization',
            field=models.ForeignKey(related_name='memberships', blank=True, to='parladata.Organization', help_text='The organization that is a party to the relationship', null=True),
        ),
        migrations.AddField(
            model_name='membership',
            name='person',
            field=models.ForeignKey(related_name='memberships', blank=True, to='parladata.Person', help_text='The person who is a party to the relationship', null=True),
        ),
        migrations.AddField(
            model_name='membership',
            name='post',
            field=models.ForeignKey(related_name='memberships', blank=True, to='parladata.Post', help_text='The post held by the person in the organization through this membership', null=True),
        ),
        migrations.AddField(
            model_name='link',
            name='membership',
            field=models.ForeignKey(blank=True, to='parladata.Membership', help_text=b'The membership of this link.', null=True),
        ),
        migrations.AddField(
            model_name='link',
            name='motion',
            field=models.ForeignKey(blank=True, to='parladata.Motion', help_text=b'The motion of this link.', null=True),
        ),
        migrations.AddField(
            model_name='link',
            name='organization',
            field=models.ForeignKey(blank=True, to='parladata.Organization', help_text=b'The organization of this link.', null=True),
        ),
        migrations.AddField(
            model_name='link',
            name='person',
            field=models.ForeignKey(blank=True, to='parladata.Person', help_text=b'The person of this link.', null=True),
        ),
        migrations.AddField(
            model_name='link',
            name='session',
            field=models.ForeignKey(blank=True, to='parladata.Session', null=True),
        ),
        migrations.AddField(
            model_name='link',
            name='tags',
            field=taggit.managers.TaggableManager(to='taggit.Tag', through='taggit.TaggedItem', help_text='A comma-separated list of tags.', verbose_name='Tags'),
        ),
        migrations.AddField(
            model_name='identifier',
            name='organization',
            field=models.ForeignKey(blank=True, to='parladata.Organization', help_text=b'The organization this identifier belongs to', null=True),
        ),
        migrations.AddField(
            model_name='identifier',
            name='person',
            field=models.ForeignKey(blank=True, to='parladata.Person', help_text=b'The person this identifier belongs to', null=True),
        ),
        migrations.AddField(
            model_name='count',
            name='vote',
            field=models.ForeignKey(blank=True, to='parladata.Vote', help_text=b'The vote of this count.', null=True),
        ),
        migrations.AddField(
            model_name='contactdetail',
            name='membership',
            field=models.ForeignKey(blank=True, to='parladata.Membership', help_text=b'The organization this name belongs to', null=True),
        ),
        migrations.AddField(
            model_name='contactdetail',
            name='organization',
            field=models.ForeignKey(blank=True, to='parladata.Organization', help_text=b'The organization this name belongs to', null=True),
        ),
        migrations.AddField(
            model_name='contactdetail',
            name='person',
            field=models.ForeignKey(blank=True, to='parladata.Person', help_text=b'The person this name belongs to', null=True),
        ),
        migrations.AddField(
            model_name='contactdetail',
            name='post',
            field=models.ForeignKey(blank=True, to='parladata.Post', help_text=b'The person this name belongs to', null=True),
        ),
        migrations.AddField(
            model_name='ballot',
            name='orgvoter',
            field=models.ForeignKey(blank=True, to='parladata.Organization', help_text=b'The voter represents and organisation.', null=True),
        ),
        migrations.AddField(
            model_name='ballot',
            name='vote',
            field=models.ForeignKey(help_text=b'The vote event', to='parladata.Vote'),
        ),
        migrations.AddField(
            model_name='ballot',
            name='voter',
            field=models.ForeignKey(blank=True, to='parladata.Person', help_text=b'The voter', null=True),
        ),
        migrations.AddField(
            model_name='ballot',
            name='voterparty',
            field=models.ForeignKey(related_name='party', default=2, to='parladata.Organization', help_text=b'The party of the voter.'),
        ),
    ]
