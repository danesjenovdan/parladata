from parlacards.serializers.common import CardSerializer
from parlacards.serializers.session import SessionSerializer


class SingleSessionCardSerializer(CardSerializer):
    def get_results(self, session):
        serializer = SessionSerializer(session, context=self.context)
        return serializer.data
