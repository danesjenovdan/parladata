from parlacards.models import SessionTfidf

from parlacards.serializers.tfidf import TfidfSerializer

from parlacards.serializers.common import SessionScoreCardSerializer


class SessionTfidfCardSerializer(SessionScoreCardSerializer):
    def get_results(self, obj):
        # obj is the session
        latest_score = (
            SessionTfidf.objects.filter(
                session=obj,
                timestamp__lte=self.context["request_date"],
            )
            .order_by("-timestamp")
            .first()
        )

        if latest_score:
            tfidf_scores = SessionTfidf.objects.filter(
                session=obj,
                timestamp=latest_score.timestamp,
            )
        else:
            tfidf_scores = []

        serializer = TfidfSerializer(
            tfidf_scores,
            many=True,
            context=self.context,
        )

        return serializer.data
