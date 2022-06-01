from importlib import import_module

from rest_framework import serializers

from parladata.models.area import Area
from parladata.models.organization import Organization
from parladata.models.memberships import PersonMembership
from parladata.models.versionable_properties import PersonName, PersonPreferredPronoun

from parlacards.models import (
    PersonAvgSpeechesPerSession,
    PersonNumberOfQuestions,
    DeviationFromGroup,
    PersonVoteAttendance,
    PersonNumberOfSpokenWords,
    PersonVocabularySize,
)

from parlacards.serializers.area import AreaSerializer
from parlacards.serializers.common import (
    CardSerializer,
    CommonPersonSerializer,
    CommonOrganizationSerializer,
)

from parlacards.pagination import create_paginator

from parlacards.utils import local_collator


class PersonAnalysesSerializer(CommonPersonSerializer):
    def calculate_cache_key(self, person):
        all_analyses = (
            PersonAvgSpeechesPerSession,
            PersonNumberOfQuestions,
            DeviationFromGroup,
            PersonVoteAttendance,
            PersonNumberOfSpokenWords,
            PersonVocabularySize,
        )

        analysis_timestamps = []
        for analysis in all_analyses:
            if analysis_object := analysis.objects.filter(person=person).order_by('-timestamp').first():
                analysis_timestamps.append(analysis_object.timestamp)

        timestamp = max([person.updated_at, *analysis_timestamps])

        return f'PersonAnalysesSerializer_{person.id}_{timestamp.isoformat()}'

    def _get_person_value(self, person, property_model_name):
        scores_module = import_module('parlacards.models')
        ScoreModel = getattr(scores_module, property_model_name)

        score_object = ScoreModel.objects.filter(
            person_id=person.id,
            timestamp__lte=self.context['date']
        ).order_by('-timestamp').first()

        if score_object:
            return score_object.value

        return None

    def _get_working_bodies(self, person):
        memberships = PersonMembership.valid_at(self.context['date']).filter(member=person)
        organizations = Organization.objects.filter(
            id__in=memberships.values_list('organization'),
            classification__in=('committee', 'commission', 'other'), # TODO: add other classifications?
        )
        organization_serializer = CommonOrganizationSerializer(
            organizations,
            context=self.context,
            many=True,
        )
        return organization_serializer.data

    def _get_districts(self, person):
        districts_serializer = AreaSerializer(
            person.districts,
            context=self.context,
            many=True,
        )
        return districts_serializer.data

    def get_results(self, person):
        return {
            'mandates': person.number_of_mandates,
            'speeches_per_session': self._get_person_value(person, 'PersonAvgSpeechesPerSession'),
            'number_of_questions': self._get_person_value(person, 'PersonNumberOfQuestions'),
            'mismatch_of_pg': self._get_person_value(person, 'DeviationFromGroup'),
            'presence_votes': self._get_person_value(person, 'PersonVoteAttendance'),
            'birth_date': person.date_of_birth.isoformat() if person.date_of_birth else None,
            'education': person.education_level,
            'spoken_words': self._get_person_value(person, 'PersonNumberOfSpokenWords'),
            'vocabulary_size': self._get_person_value(person, 'PersonVocabularySize'),
            'working_bodies': self._get_working_bodies(person),
            'districts': self._get_districts(person),
        }

    results = serializers.SerializerMethodField()

class MiscMembersCardSerializer(CardSerializer):
    model_fields_mapping = {
        'birth_date': 'date_of_birth',
    }

    versionable_models_mapping = {
        'name': ('PersonName', 'value'),
        'mandates': ('PersonNumberOfMandates', 'value'),
        'education': ('PersonEducationLevel', 'education_level__text'),
    }

    score_models_mapping = {
        'speeches_per_session': 'PersonAvgSpeechesPerSession',
        'number_of_questions': 'PersonNumberOfQuestions',
        'mismatch_of_pg': 'DeviationFromGroup',
        'presence_votes': 'PersonVoteAttendance',
        'spoken_words': 'PersonNumberOfSpokenWords',
        'vocabulary_size': 'PersonVocabularySize',
    }

    def _groups(self, playing_field, timestamp):
        '''Returns serialized parliamentary groups.'''
        organizations = playing_field.query_parliamentary_groups(timestamp)
        organization_serializer = CommonOrganizationSerializer(
            organizations,
            context=self.context,
            many=True,
        )
        return organization_serializer.data

    def _working_bodies(self, timestamp):
        memberships = PersonMembership.valid_at(timestamp)
        organizations = Organization.objects.filter(
            id__in=memberships.values_list('organization'),
            classification__in=('committee', 'commission', 'other'), # TODO: add other classifications?
        )
        organization_serializer = CommonOrganizationSerializer(
            organizations,
            context=self.context,
            many=True,
        )
        return organization_serializer.data

    def _districts(self, timestamp):
        memberships = PersonMembership.valid_at(timestamp)
        districts = Area.objects.filter(
            candidates__in=memberships.values_list('member'),
            classification='district',
        ).distinct('id')
        district_serializer = AreaSerializer(
            districts,
            context=self.context,
            many=True,
        )
        return district_serializer.data

    def _maximum_score(self, model_name, people):
        scores_module = import_module('parlacards.models')
        ScoreModel = getattr(scores_module, model_name)

        latest_scores = ScoreModel.objects.filter(person__in=people) \
            .order_by('person', '-timestamp') \
            .distinct('person') \
            .values_list('value', flat=True)

        if latest_scores.count() > 0:
            return max(latest_scores)
        else:
            return 0

    def _maximum_scores(self, playing_field, timestamp):
        people = playing_field.query_voters(timestamp)

        score_maximum_values = {
            key: self._maximum_score(model_name, people)
            for key, model_name in self.score_models_mapping.items()
        }

        return score_maximum_values

    def _filtered_and_ordered_people(self, playing_field, timestamp):
        group_ids = list(filter(lambda x: x.isdigit(), self.context.get('GET', {}).get('groups', '').split(',')))
        working_body_ids = list(filter(lambda x: x.isdigit(), self.context.get('GET', {}).get('working_bodies', '').split(',')))
        district_ids = list(filter(lambda x: x.isdigit(), self.context.get('GET', {}).get('districts', '').split(',')))
        preferred_pronoun = self.context.get('GET', {}).get('preferred_pronoun', None)

        people = playing_field.query_voters(timestamp)

        # filter by preferred pronouns
        if preferred_pronoun is not None:
            member_ids = PersonPreferredPronoun.objects.valid_at(timestamp) \
                .filter(owner__in=people, value=preferred_pronoun) \
                .values_list('owner', flat=True)
            people = people.filter(id__in=member_ids)

        # filter by group ids
        if len(group_ids) > 0:
            member_ids = PersonMembership.valid_at(timestamp).filter(
                organization=playing_field,
                role='voter',
                member_id__in=people,
                on_behalf_of__in=group_ids,
            ).values_list('member', flat=True)
            people = people.filter(id__in=member_ids)

        # filter by working body ids
        if len(working_body_ids) > 0:
            member_ids = PersonMembership.valid_at(timestamp).filter(
                organization__classification__in=('committee', 'commission', 'other'), # TODO: add other classifications?
                member_id__in=people,
                organization_id__in=working_body_ids,
            ).values_list('member', flat=True)
            people = people.filter(id__in=member_ids)

        # filter by district ids
        if len(district_ids) > 0:
            people = people.filter(districts__id__in=district_ids)

        # filter by name text search
        if text := self.context.get('GET', {}).get('text', None):
            people_ids = PersonName.objects.filter(
                owner__in=people,
                value__icontains=text
            ).valid_at(
                timestamp
            ).values_list('owner', flat=True)
            people = people.filter(id__in=people_ids)

        # get order from url
        order_by = self.context.get('GET', {}).get('order_by', 'name')
        order_reverse = False

        # determine if order should be reversed
        if order_by.startswith('-'):
            order_by = order_by[1:]
            order_reverse = True

        # order by model field
        field_name_to_order_by = self.model_fields_mapping.get(order_by, None)
        if field_name_to_order_by:
            order_string = f'-{field_name_to_order_by}' if order_reverse else field_name_to_order_by
            return people.order_by(order_string, 'id')

        # order by versionable property model
        versionable_model_tuple = self.versionable_models_mapping.get(order_by, None)
        if versionable_model_tuple:
            versionable_model_name, versionable_field_name = versionable_model_tuple
            versionable_properties_module = import_module('parladata.models.versionable_properties')
            PropertyModel = getattr(versionable_properties_module, versionable_model_name)

            active_properties = PropertyModel.objects.valid_at(timestamp) \
                .filter(owner__in=people) \
                .order_by('owner', '-valid_from') \
                .distinct('owner') \
                .values('owner', versionable_field_name)

            is_number_field = len(active_properties) and isinstance(active_properties[0].get(versionable_field_name), (int, float))
            properties_by_owner_id = {prop['owner']: prop for prop in active_properties}

            def get_property_value(owner_id, default=0):
                return properties_by_owner_id.get(owner_id, {versionable_field_name: default})[versionable_field_name]

            def get_sort_key(person):
                if is_number_field:
                    return get_property_value(person.id, default=0)
                return local_collator.getSortKey(get_property_value(person.id, default=''))

            return list(sorted(list(people), key=get_sort_key, reverse=order_reverse))

        # order by score model
        score_model_name = self.score_models_mapping.get(order_by, None)

        if score_model_name:
            scores_module = import_module('parlacards.models')
            ScoreModel = getattr(scores_module, score_model_name)

            latest_scores = ScoreModel.objects.filter(person__in=people) \
                .order_by('person', '-timestamp') \
                .distinct('person') \
                .values('person', 'value')

            people_by_id = {person.id: person for person in people}
            sorted_scores = sorted(list(latest_scores), key=lambda s: s['value'], reverse=order_reverse)
            return [people_by_id[s['person']] for s in sorted_scores]

        return people.order_by('id')

    def get_results(self, parent_organization):
        return {
            'groups': self._groups(parent_organization, self.context['date']),
            'working_bodies': self._working_bodies(self.context['date']),
            'districts': self._districts(self.context['date']),
            'maximum_scores': self._maximum_scores(parent_organization, self.context['date']),
        }

    def to_representation(self, parent_organization):
        parent_data = super().to_representation(parent_organization)

        ordered_people = self._filtered_and_ordered_people(parent_organization, self.context['date'])

        paged_object_list, pagination_metadata = create_paginator(self.context.get('GET', {}), ordered_people, prefix='members:')

        # serialize people
        people_serializer = PersonAnalysesSerializer(
            paged_object_list,
            many=True,
            context=self.context
        )

        return {
            **parent_data,
            **pagination_metadata,
            'results': {
                **parent_data['results'],
                'members': people_serializer.data,
            },
        }
