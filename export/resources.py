from import_export.resources import ModelResource
from import_export.fields import Field

from parladata.models import Person, Vote
from parlacards.models import GroupDiscord, PersonNumberOfSpokenWords


class MPResource(ModelResource):
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


class VoteResource(ModelResource):
    class Meta:
        model = Vote
        fields = ('id', 'name', 'motion__text', 'motion__summary', 'result',)
        export_order = ('id', 'name', 'motion__text', 'motion__summary', 'result',)


class GroupDiscordResource(ModelResource):
    name = Field()

    class Meta:
        model = GroupDiscord
        fields = ('name', 'value', 'timestamp',)
        export_order = ('name', 'value', 'timestamp',)
    
    def dehydrate_name(self, score):
        return score.group.name


class PersonNumberOfSpokenWordsResource(ModelResource):
    name = Field()

    class Meta:
        model = PersonNumberOfSpokenWords
        fields = ('name', 'value', 'timestamp',)
        export_order = ('name', 'value', 'timestamp',)
    
    def dehydrate_name(self, score):
        return score.person.name
