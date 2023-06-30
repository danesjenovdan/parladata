from datetime import datetime, timedelta

from django.db.models import Q

from import_export.fields import Field

from export.resources.common import ExportModelResource, get_cached_person_name

from parladata.models import (
    Person,
    Vote,
    Mandate,
    Law,
    Session,
    PersonMembership,
    Organization,
    OrganizationMembership,
    PublicPersonQuestion,
    Ballot,
    Question,
)
from parlacards.models import (
    DeviationFromGroup,
    GroupDiscord,
    GroupNumberOfQuestions,
    GroupVocabularySize,
    GroupVoteAttendance,
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
from parladata.models.person import Person


class MPResource(ExportModelResource):
    def get_queryset(self, mandate_id=None):
        """
        Returns a queryset of all parliament members for given mandate id.
        Or returns all persons if there is no mandate id.
        """
        if not mandate_id:
            mandate_id = Mandate.objects.last()
        try:
            mandate = Mandate.objects.get(id=mandate_id)
            from_timestamp, to_timestamp = mandate.get_time_range_from_mandate(datetime.now())
            before_end = to_timestamp-timedelta(minutes=1)
            root_organization, playing_field = mandate.query_root_organizations(before_end)
            members = playing_field.query_members(before_end)
            self.people = playing_field.query_voters(before_end)
            self.playing_field = playing_field
            return members
        # if mandate does not exist return empty queryset
        except:
            self.people = None
            self.playing_field = None
            return Person.objects.none()


    name = Field()
    age = Field()
    education_level = Field()
    preferred_pronoun = Field()
    number_of_mandates = Field()

    speeches_per_session = Field()
    number_of_questions = Field()
    mismatch_of_pg = Field()
    presence_votes = Field()
    spoken_words = Field()
    vocabulary_size = Field()

    class Meta:
        model = Person
        fields = (
            'id',
            'name',
            'date_of_birth',
            'age',
            'education_level',
            'preferred_pronoun',
            'number_of_mandates',

            'speeches_per_session',
            'number_of_questions',
            'mismatch_of_pg',
            'presence_votes',
            'spoken_words',
            'vocabulary_size',
        )
        export_order = (
            'id',
            'name',
            'date_of_birth',
            'age',
            'education_level',
            'preferred_pronoun',
            'number_of_mandates',

            'speeches_per_session',
            'number_of_questions',
            'mismatch_of_pg',
            'presence_votes',
            'spoken_words',
            'vocabulary_size',
        )

    def dehydrate_name(self, person):
        return person.name

    def dehydrate_age(self, person):
        if person.date_of_birth:
            return int((datetime.now().date() - person.date_of_birth).days / 365.2425)
        return None

    def get_score(self, ScoreModel, person):
        latest_scores = ScoreModel.objects.filter(
                person=person,
            ) \
            .order_by('-timestamp') \
            .latest('created_at')
        if latest_scores:
            return latest_scores.value
        else:
            return None

    def dehydrate_education_level(self, person):
        return person.education_level

    def dehydrate_preferred_pronoun(self, person):
        return person.preferred_pronoun

    def dehydrate_number_of_mandates(self, person):
        return person.number_of_mandates

    def dehydrate_speeches_per_session(self, person):
        return self.get_score(PersonAvgSpeechesPerSession, person)

    def dehydrate_number_of_questions(self, person):
        return self.get_score(PersonNumberOfQuestions, person)

    def dehydrate_mismatch_of_pg(self, person):
        return self.get_score(DeviationFromGroup, person)

    def dehydrate_presence_votes(self, person):
        return self.get_score(PersonVoteAttendance, person)

    def dehydrate_spoken_words(self, person):
        return self.get_score(PersonNumberOfSpokenWords, person)

    def dehydrate_vocabulary_size(self, person):
        return self.get_score(PersonVocabularySize, person)



class GroupsResource(ExportModelResource):
    def get_queryset(self, mandate_id=None, request_id=None):
        """
        Returns a queryset of all parliament groups for given mandate id.
        Or returns all groups if there is no mandate id.
        """
        if mandate_id:
            try:
                mandate = Mandate.objects.get(id=mandate_id)
                from_timestamp, to_timestamp = mandate.get_time_range_from_mandate(datetime.now())
                before_end = to_timestamp-timedelta(minutes=1)
                root_organization, playing_field = mandate.query_root_organizations(before_end)
                organizations = playing_field.query_organization_members(before_end)
                return organizations
            # if mandate does not exist return empty queryset
            except:
                return Organization.objects.none()
        else:
            memberships = OrganizationMembership.objects.filter(organization__classification='root').values_list('member__id', flat=True)
            return Organization.objects.filter(id__in=memberships)

    name = Field()
    acronym = Field()
    number_of_organization_members_at = Field()
    intra_disunion = Field()
    vocabulary_size = Field()
    number_of_questions = Field()
    vote_attendance = Field()

    class Meta:
        model = Organization
        fields = (
            'id',
            'name',
            'acronym',
            'number_of_organization_members_at',
            'intra_disunion',
            'vocabulary_size',
            'number_of_questions',
            'vote_attendance',)
        export_order = ('id', 'name', 'acronym', 'number_of_organization_members_at')

    def get_group_score(self, ScoreModel, group):
        latest_scores = ScoreModel.objects.filter(
            group_id=group.id
        ) \
        .order_by('-timestamp') \
        .latest('created_at')

        if latest_scores:
            return latest_scores.value
        return None

    def dehydrate_name(self, organization):
        return organization.name

    def dehydrate_acronym(self, organization):
        return organization.acronym

    def dehydrate_number_of_organization_members_at(self, organization):
        return organization.number_of_organization_members_at()

    def dehydrate_intra_disunion(self, organization):
        return self.get_group_score(GroupDiscord, organization)

    def dehydrate_vocabulary_size(self, organization):
        return self.get_group_score(GroupVocabularySize, organization)

    def dehydrate_number_of_questions(self, organization):
        return self.get_group_score(GroupNumberOfQuestions, organization)

    def dehydrate_vote_attendance(self, organization):
        return self.get_group_score(GroupVoteAttendance, organization)


class MembershipResource(ExportModelResource):
    def get_queryset(self, mandate_id=None, request_id=None):
        """
        Returns a queryset of all memberships for given mandate id.
        Or returns all memberships if there is no mandate id.
        """
        if mandate_id:
            votes = PersonMembership.objects.filter(
                mandate=mandate_id
            )
            return votes
        else:
            return PersonMembership.objects.all()

    member = Field()
    start_time = Field()
    end_time = Field()
    organization = Field()
    on_behalf_of = Field()
    role = Field()

    class Meta:
        model = PersonMembership
        fields = ('id', 'start_time', 'end_time', 'organization', 'on_behalf_of', 'member', 'role')
        export_order = ('id', 'start_time', 'end_time', 'organization', 'on_behalf_of', 'member', 'role')

    def dehydrate_member(self, membership):
        return membership.member.name if membership.member else None

    def dehydrate_organization(self, membership):
        return membership.organization.name if membership.organization else None

    def dehydrate_on_behalf_of(self, membership):
        return membership.on_behalf_of.name if membership.on_behalf_of else None


class SessionResource(ExportModelResource):
    def get_queryset(self, mandate_id=None, request_id=None):
        """
        Returns a queryset of all sessions for given mandate id.
        Or returns all sessions if there is no mandate id.
        """
        if mandate_id:
            sessions = Session.objects.filter(
                session__mandate=mandate_id
            )
            return sessions
        else:
            return Session.objects.all()

    organizations = Field()

    class Meta:
        model = Session
        fields = ('id', 'name', 'organizations', 'start_time', 'classification', 'in_review')
        export_order = ('id', 'name', 'organizations', 'start_time', 'classification', 'in_review')

    def dehydrate_organizations(self, session):
        return ' & '.join(list(session.organizations.values_list('latest_name', flat=True)))


class VoteResource(ExportModelResource):
    def get_queryset(self, mandate_id=None, request_id=None):
        """
        Returns a queryset of all votes for given mandate id.
        Or returns all votes if there is no mandate id.
        """
        if mandate_id:
            votes = Vote.objects.filter(
                motion__session__mandate_id=mandate_id
            )
            return votes
        else:
            return Vote.objects.all()

    law_id = Field()

    class Meta:
        model = Vote
        fields = ('id', 'name', 'motion__text', 'motion__summary', 'result', 'law_id')
        export_order = ('id', 'name', 'motion__text', 'motion__summary', 'result', 'law_id')

    def dehydrate_law_id(self, vote):
        return vote.motion.law.id


class LegislationResource(ExportModelResource):
    def get_queryset(self, mandate_id=None, request_id=None):
        """
        Returns a queryset of legislation for given mandate id.
        Or returns all legislation if there is no mandate id.
        """
        if mandate_id:
            legislation = Law.objects.filter(
                Q(legislationconsideration__session__mandate_id=mandate_id) |
                Q(mandate_id=mandate_id)
            )
            return legislation
        else:
            return Law.objects.all()

    classification = Field()
    procedure_phase = Field()
    text = Field()
    epa = Field()
    passed = Field()
    timestamp = Field()
    classification = Field()

    class Meta:
        model = Law
        fields = ('id', 'text', 'epa', 'passed', 'classification', 'timestamp', 'procedure_phase')
        export_order = ('id', 'text', 'epa', 'passed', 'classification', 'timestamp', 'procedure_phase')

    def dehydrate_classification(self, legislation):
        return legislation.classification.name if legislation.classification else ''

    def dehydrate_procedure_phase(self, legislation):
        procedure_phase = legislation.considerations.last()
        if procedure_phase:
            return procedure_phase.name
        else:
            return ''

    def dehydrate_text(self, legislation):
        return legislation.text

    def dehydrate_passed(self, legislation):
        return legislation.passed

    def dehydrate_epa(self, legislation):
        return legislation.epa

    def dehydrate_timestamp(self, legislation):
        return legislation.timestamp.isoformat() if legislation.timestamp else ''


# CARDS

# class GroupDiscordResource(CardExport):
#     name = Field()

#     class Meta:
#         model = GroupDiscord
#         fields = ('name', 'value', 'timestamp',)
#         export_order = ('name', 'value', 'timestamp',)

#     def dehydrate_name(self, score):
#         return score.group.name

# class PersonCardExport(CardExport):
#     name = Field()

#     def get_queryset(self, mandate_id=None, request_id=None):
#         queryset = super().get_queryset(mandate_id=mandate_id)
#         return queryset.filter(person_id=request_id).order_by('-timestamp')


#     def dehydrate_name(self, score):
#         return get_cached_person_name(score.person_id)

#     class Meta:
#         fields = ('name', 'value', 'timestamp',)
#         export_order = ('name', 'value', 'timestamp',)


# class PersonNumberOfSpokenWordsResource(PersonCardExport):
#     class Meta:
#         model = PersonNumberOfSpokenWords


# class VocabularySizeResource(PersonCardExport):
#     class Meta:
#         model = PersonVocabularySize


# class DeviationFromGroupResource(PersonCardExport):
#     class Meta:
#         model = DeviationFromGroup


# class PersonMonthlyVoteAttendanceResource(PersonCardExport):
#     class Meta:
#         model = PersonMonthlyVoteAttendance


# class PersonPersonVoteAttendanceResource(PersonCardExport):
#     class Meta:
#         model = PersonVoteAttendance


# class ExportPersonStyleScoresResource(PersonCardExport):
#     class Meta:
#         model = PersonStyleScore
#         fields = ('name', 'style', 'value', 'timestamp',)
#         export_order = ('name', 'style', 'value', 'timestamp',)

#     def dehydrate_style(self, score):
#         return score.style


# class ExportPersonAvgSpeechesPerSessionResource(PersonCardExport):
#     class Meta:
#         model = PersonAvgSpeechesPerSession


# class VotingDistanceResource(PersonCardExport):
#     distance_with = Field()
#     class Meta:
#         model = VotingDistance
#         fields = ('name', 'distance_with', 'value', 'timestamp',)
#         export_order = ('name', 'distance_with', 'value', 'timestamp',)

#     def dehydrate_distance_with(self, score):
#         return get_cached_person_name(score.target_id)


# class PersonNumberOfQuestionsResource(PersonCardExport):
#     class Meta:
#         model = PersonNumberOfQuestions


# class PersonPublicQuestionsResource(CardExport):
#     name = Field()
#     created_at = Field()
#     approved_at = Field()
#     text = Field()
#     answer_text = Field()
#     answer_at = Field()

#     def get_queryset(self, mandate_id=None, request_id=None):
#         queryset = super().get_queryset(mandate_id=mandate_id)
#         return queryset.filter(recipient_person_id=request_id).order_by('-timestamp')

#     class Meta:
#         model = PublicPersonQuestion
#         fields = ('name', 'created_at', 'approved_at', 'text', 'answer_text', 'answer_at')
#         export_order = ('name', 'created_at', 'approved_at', 'text', 'answer_text', 'answer_at')

#     def dehydrate_name(self, obj):
#         return get_cached_person_name(obj.recipient_person_id)

#     def dehydrate_answer_text(self, obj):
#         answer = obj.answer.first()
#         if answer:
#             return answer.text
#         return ''

#     def dehydrate_answer_at(self, obj):
#         answer = obj.answer.first()
#         if answer:
#             return answer.created_at.isoformat()
#         return ''


# class PersonTfidfResource(PersonCardExport):
#     token = Field()
#     class Meta:
#         model = PersonTfidf
#         fields = ('name', 'value', 'token', 'timestamp',)
#         export_order = ('name', 'value', 'token', 'timestamp',)


# class PersonMembershipResource(CardExport):
#     name = Field()
#     organization = Field()
#     on_behalf_of = Field()
#     start_time = Field()
#     end_time = Field()
#     mandate = Field()

#     def get_queryset(self, mandate_id=None, request_id=None):
#         queryset = self._meta.model.objects.filter(mandate_id=mandate_id)
#         queryset = queryset.filter(member_id=request_id).order_by('-start_time')
#         return queryset

#     def dehydrate_name(self, membership):
#         return get_cached_person_name(membership.member_id)

#     def dehydrate_organization(self, membership):
#         return membership.organization.name

#     def dehydrate_on_behalf_of(self, membership):
#         return membership.on_behalf_of.name if membership.on_behalf_of else None

#     def dehydrate_start_time(self, membership):
#         return membership.start_time.isoformat() if membership.start_time else None

#     def dehydrate_end_time(self, membership):
#         return membership.end_time.isoformat() if membership.end_time else None

#     def dehydrate_mandate(self, membership):
#         return membership.mandate.description if membership.mandate else None

#     class Meta:
#         model = PersonMembership
#         fields = ('name', 'role', 'organization', 'on_behalf_of', 'start_time', 'end_time', 'mandate')
#         export_order = ('name', 'role', 'organization', 'on_behalf_of', 'start_time', 'end_time', 'mandate')


# class PersonBallotsResource(CardExport):
#     name = Field()
#     vote_text = Field()
#     timestamp = Field()
#     passed = Field()

#     def get_queryset(self, mandate_id=None, request_id=None):
#         queryset = self._meta.model.objects.filter(vote__motion__session__mandate_id=mandate_id)
#         queryset = queryset.filter(personvoter_id=request_id).order_by('-vote__timestamp')
#         return queryset

#     def dehydrate_name(self, ballot):
#         return get_cached_person_name(ballot.personvoter_id)

#     def dehydrate_vote_text(self, ballot):
#         return ballot.vote.name

#     def dehydrate_timestamp(self, ballot):
#         return ballot.vote.timestamp.isoformat() if ballot.vote.timestamp else None

#     def dehydrate_passed(self, ballot):
#         return ballot.vote.motion.result

#     class Meta:
#         model = Ballot
#         fields = ('name', 'vote_text', 'option', 'timestamp', 'passed')
#         export_order = ('name', 'vote_text', 'option', 'timestamp', 'passed')


# class PersonQuestionsResource(CardExport):
#     authors = Field()
#     recipient_people = Field()
#     timestamp = Field()

#     def get_queryset(self, mandate_id=None, request_id=None):
#         queryset = self._meta.model.objects.filter(mandate_id=mandate_id)
#         queryset = queryset.filter(person_authors__id=request_id).order_by('-timestamp')
#         print(queryset)
#         return queryset

#     def dehydrate_authors(self, question):
#         return ', '.join([get_cached_person_name(author.id) for author in question.person_authors.all()])

#     def dehydrate_recipient_people(self, question):
#         return ', '.join([get_cached_person_name(recipient.id) for recipient in question.recipient_people.all()])

#     def dehydrate_timestamp(self, question):
#         return question.timestamp.isoformat() if question.timestamp else None


#     class Meta:
#         model = Question
#         fields = ('authors', 'title', 'type_of_question', 'recipient_people', 'recipient_text', 'timestamp')
#         export_order = ('authors', 'title', 'type_of_question', 'recipient_people', 'recipient_text', 'timestamp')
