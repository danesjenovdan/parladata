from django.db.models.functions import TruncDay

from parladata.models.question import Question

from parlacards.serializers.common import PersonScoreCardSerializer
from parlacards.serializers.recent_activity import DailyActivitySerializer

class PersonQuestionCardSerializer(PersonScoreCardSerializer):
    def get_results(self, obj):
        # obj is the person
        questions = Question.objects.filter(
            person_authors=obj,
            timestamp__lte=self.context['date']
        ).order_by(
            '-timestamp'
        ).annotate(
            date=TruncDay('timestamp')
        )

        dates_to_serialize = sorted(set(questions.values_list('date', flat=True)), reverse=True)

        # this is ripe for optimization
        # currently iterates over all questions
        # for every date
        grouped_questions_to_serialize = [
            {
                'date': date,
                'events': questions.filter(
                    date=date
                ).order_by('-timestamp')
            } for date in dates_to_serialize
        ]

        serializer = DailyActivitySerializer(
            grouped_questions_to_serialize,
            many=True,
            context=self.context
        )
        return serializer.data
