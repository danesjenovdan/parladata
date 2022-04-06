import tablib
from datetime import datetime

from django.db.models.query import QuerySet

from import_export.resources import ModelResource
from import_export.fields import Field

from parladata.models import Person, Vote
from parlacards.models import GroupDiscord, PersonNumberOfSpokenWords


class ExportModelResource(ModelResource):
    """
    Extends ModelResource class with additional functions that allow exporting data from admin using a generator.
    """
    def export_as_generator_csv(self, queryset=None, mandate_id=None, *args, **kwargs):
        """
        Generator function that returns queryset in csv format.
        """
        self.before_export(queryset, *args, **kwargs)
        if queryset is None:
            queryset = self.get_queryset(mandate_id=mandate_id)
        headers = self.get_export_headers()
        data = tablib.Dataset(headers=headers)
        # write headers
        yield data.csv

        if isinstance(queryset, QuerySet):
            # Iterate without the queryset cache, to avoid wasting memory when
            # exporting large datasets.
            iterable = queryset.iterator()
        else:
            iterable = queryset
        for obj in iterable:
            # Return subset of the data (one row)
            data = tablib.Dataset()
            data.append(self.export_resource(obj))
            yield data.csv

        self.after_export(queryset, data, *args, **kwargs)

        yield '\n'
    
    def export_as_generator_json(self, queryset=None, mandate_id=None, *args, **kwargs):
        """
        Generator function that returns queryset in json format.
        """
        self.before_export(queryset, *args, **kwargs)
        if queryset is None:
            queryset = self.get_queryset(mandate_id=mandate_id)
        headers = self.get_export_headers()
        # no need to yield headers because this is json
        # but we do yield start of list
        yield '['

        if isinstance(queryset, QuerySet):
            # Iterate without the queryset cache, to avoid wasting memory when
            # exporting large datasets.
            iterable = queryset.iterator()
        else:
            iterable = queryset
        for index, obj in enumerate(iterable):
            # Return subset of the data (one row)
            # here Dataset needs headers to create json keys
            data = tablib.Dataset(headers=headers)
            data.append(self.export_resource(obj))
            # data.json will return a LIST of object(s) for each iteration
            # so we cut out first '[' and last ']' and add comma
            if (index != 0):
                yield ','
            yield data.json[1:-1]
            # note to self: should probably think of something less hacky

        self.after_export(queryset, data, *args, **kwargs)

        # close list at the end
        yield ']'


class MPResource(ExportModelResource):
    name = Field()
    age = Field()
    education_level = Field()
    preferred_pronoun = Field()
    number_of_mandates = Field()

    class Meta:
        model = Person
        fields = ('id', 'name', 'date_of_birth', 'age', 'education_level', 'preferred_pronoun', 'number_of_mandates',)
        export_order = ('id', 'name', 'date_of_birth', 'age', 'education_level', 'preferred_pronoun', 'number_of_mandates',)
    
    def dehydrate_name(self, person):
        return person.name

    def dehydrate_age(self, person):
        if person.date_of_birth:
            return int((datetime.now().date() - person.date_of_birth).days / 365.2425)
        return None
    
    def dehydrate_education_level(self, person):
        return person.education_level
    
    def dehydrate_preferred_pronoun(self, person):
        return person.preferred_pronoun
    
    def dehydrate_number_of_mandates(self, person):
        return person.number_of_mandates


class VoteResource(ExportModelResource):
    def get_queryset(self, mandate_id=None):
        """
        Returns a queryset of all votes for given mandate id.
        Or returns all votes if there is no mandate id.
        """
        if mandate_id:
            votes = Vote.objects.filter(
                motion__session__mandate=mandate_id
            )
            return votes
        else:
            return Vote.objects.all()
    
    class Meta:
        model = Vote
        fields = ('id', 'name', 'motion__text', 'motion__summary', 'result',)
        export_order = ('id', 'name', 'motion__text', 'motion__summary', 'result',)


class GroupDiscordResource(ExportModelResource):
    name = Field()

    class Meta:
        model = GroupDiscord
        fields = ('name', 'value', 'timestamp',)
        export_order = ('name', 'value', 'timestamp',)
    
    def dehydrate_name(self, score):
        return score.group.name


class PersonNumberOfSpokenWordsResource(ExportModelResource):
    name = Field()

    class Meta:
        model = PersonNumberOfSpokenWords
        fields = ('name', 'value', 'timestamp',)
        export_order = ('name', 'value', 'timestamp',)
    
    def dehydrate_name(self, score):
        return score.person.name
