from parlacards.pagination import create_paginator
from parlacards.serializers.common import PersonScoreCardSerializer
from parlacards.serializers.question import QuestionSerializer
from parladata.models.question import Question


class PersonQuestionCardSerializer(PersonScoreCardSerializer):
    def get_results(self, person):
        # this is implemeted in to_representation for pagination
        return None

    def to_representation(self, person):
        parent_data = super().to_representation(person)

        questions = Question.objects.filter(person_authors=person, timestamp__lte=self.context['date']) \
            .order_by('-timestamp')

        paged_object_list, pagination_metadata = create_paginator(self.context.get('GET', {}), questions)

        questions_serializer = QuestionSerializer(
            paged_object_list,
            many=True,
            context=self.context,
        )

        return {
            **parent_data,
            **pagination_metadata,
            'results': questions_serializer.data,
        }
