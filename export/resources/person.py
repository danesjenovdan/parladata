from import_export.fields import Field

from parladata.models import (
    PersonMembership,
    PublicPersonQuestion,
    Ballot,
    Question,
)
from parlacards.models import (
    DeviationFromGroup,
    PersonAvgSpeechesPerSession,
    PersonNumberOfQuestions,
    PersonNumberOfSpokenWords,
    PersonVocabularySize,
    PersonVoteAttendance,
    PersonMonthlyVoteAttendance,
    PersonStyleScore,
    VotingDistance,
    PersonTfidf,
)

from export.resources.common import CardExport, get_cached_person_name


class PersonCardExport(CardExport):
    name = Field()

    def get_queryset(self, mandate_id=None, request_id=None):
        queryset = super().get_queryset(mandate_id=mandate_id)
        return queryset.filter(person_id=request_id).order_by('-timestamp')

    def dehydrate_name(self, score):
        return get_cached_person_name(score.person_id)

    class Meta:
        fields = ('name', 'value', 'timestamp',)
        export_order = ('name', 'value', 'timestamp',)


class PersonNumberOfSpokenWordsResource(PersonCardExport):
    class Meta:
        model = PersonNumberOfSpokenWords


class VocabularySizeResource(PersonCardExport):
    class Meta:
        model = PersonVocabularySize


class DeviationFromGroupResource(PersonCardExport):
    class Meta:
        model = DeviationFromGroup


class PersonMonthlyVoteAttendanceResource(PersonCardExport):
    class Meta:
        model = PersonMonthlyVoteAttendance


class PersonPersonVoteAttendanceResource(PersonCardExport):
    class Meta:
        model = PersonVoteAttendance


class ExportPersonStyleScoresResource(PersonCardExport):
    class Meta:
        model = PersonStyleScore
        fields = ('name', 'style', 'value', 'timestamp',)
        export_order = ('name', 'style', 'value', 'timestamp',)

    def dehydrate_style(self, score):
        return score.style


class ExportPersonAvgSpeechesPerSessionResource(PersonCardExport):
    class Meta:
        model = PersonAvgSpeechesPerSession


class VotingDistanceResource(PersonCardExport):
    distance_with = Field()
    class Meta:
        model = VotingDistance
        fields = ('name', 'distance_with', 'value', 'timestamp',)
        export_order = ('name', 'distance_with', 'value', 'timestamp',)

    def dehydrate_distance_with(self, score):
        return get_cached_person_name(score.target_id)


class PersonNumberOfQuestionsResource(PersonCardExport):
    class Meta:
        model = PersonNumberOfQuestions


class PersonPublicQuestionsResource(CardExport):
    name = Field()
    created_at = Field()
    approved_at = Field()
    text = Field()
    answer_text = Field()
    answer_at = Field()

    def get_queryset(self, mandate_id=None, request_id=None):
        queryset = super().get_queryset(mandate_id=mandate_id)
        return queryset.filter(recipient_person_id=request_id).order_by('-timestamp')

    class Meta:
        model = PublicPersonQuestion
        fields = ('name', 'created_at', 'approved_at', 'text', 'answer_text', 'answer_at')
        export_order = ('name', 'created_at', 'approved_at', 'text', 'answer_text', 'answer_at')

    def dehydrate_name(self, obj):
        return get_cached_person_name(obj.recipient_person_id)

    def dehydrate_answer_text(self, obj):
        answer = obj.answer.first()
        if answer:
            return answer.text
        return ''

    def dehydrate_answer_at(self, obj):
        answer = obj.answer.first()
        if answer:
            return answer.created_at.isoformat()
        return ''


class PersonTfidfResource(PersonCardExport):
    token = Field()
    class Meta:
        model = PersonTfidf
        fields = ('name', 'value', 'token', 'timestamp',)
        export_order = ('name', 'value', 'token', 'timestamp',)


class PersonMembershipResource(CardExport):
    name = Field()
    organization = Field()
    on_behalf_of = Field()
    start_time = Field()
    end_time = Field()
    mandate = Field()

    def get_queryset(self, mandate_id=None, request_id=None):
        queryset = self._meta.model.objects.filter(mandate_id=mandate_id)
        queryset = queryset.filter(member_id=request_id).order_by('-start_time')
        return queryset

    def dehydrate_name(self, membership):
        return get_cached_person_name(membership.member_id)

    def dehydrate_organization(self, membership):
        return membership.organization.name

    def dehydrate_on_behalf_of(self, membership):
        return membership.on_behalf_of.name if membership.on_behalf_of else None

    def dehydrate_start_time(self, membership):
        return membership.start_time.isoformat() if membership.start_time else None

    def dehydrate_end_time(self, membership):
        return membership.end_time.isoformat() if membership.end_time else None

    def dehydrate_mandate(self, membership):
        return membership.mandate.description if membership.mandate else None

    class Meta:
        model = PersonMembership
        fields = ('name', 'role', 'organization', 'on_behalf_of', 'start_time', 'end_time', 'mandate')
        export_order = ('name', 'role', 'organization', 'on_behalf_of', 'start_time', 'end_time', 'mandate')


class PersonBallotsResource(CardExport):
    name = Field()
    vote_text = Field()
    timestamp = Field()
    passed = Field()

    def get_queryset(self, mandate_id=None, request_id=None):
        queryset = self._meta.model.objects.filter(vote__motion__session__mandate_id=mandate_id)
        queryset = queryset.filter(personvoter_id=request_id).order_by('-vote__timestamp')
        return queryset

    def dehydrate_name(self, ballot):
        return get_cached_person_name(ballot.personvoter_id)

    def dehydrate_vote_text(self, ballot):
        return ballot.vote.name

    def dehydrate_timestamp(self, ballot):
        return ballot.vote.timestamp.isoformat() if ballot.vote.timestamp else None

    def dehydrate_passed(self, ballot):
        return ballot.vote.motion.result

    class Meta:
        model = Ballot
        fields = ('name', 'vote_text', 'option', 'timestamp', 'passed')
        export_order = ('name', 'vote_text', 'option', 'timestamp', 'passed')


class PersonQuestionsResource(CardExport):
    authors = Field()
    recipient_people = Field()
    timestamp = Field()

    def get_queryset(self, mandate_id=None, request_id=None):
        queryset = self._meta.model.objects.filter(mandate_id=mandate_id)
        queryset = queryset.filter(person_authors__id=request_id).order_by('-timestamp')
        print(queryset)
        return queryset

    def dehydrate_authors(self, question):
        return ', '.join([get_cached_person_name(author.id) for author in question.person_authors.all()])

    def dehydrate_recipient_people(self, question):
        return ', '.join([get_cached_person_name(recipient.id) for recipient in question.recipient_people.all()])

    def dehydrate_timestamp(self, question):
        return question.timestamp.isoformat() if question.timestamp else None


    class Meta:
        model = Question
        fields = ('authors', 'title', 'type_of_question', 'recipient_people', 'recipient_text', 'timestamp')
        export_order = ('authors', 'title', 'type_of_question', 'recipient_people', 'recipient_text', 'timestamp')
