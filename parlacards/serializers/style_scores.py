from rest_framework import serializers

from parlacards.serializers.common import CommonSerializer

from parlacards.models import PersonStyleScore

class StyleScoresSerializer(CommonSerializer):
    def get_style_score(self, person, style):
        score = PersonStyleScore.objects.filter(
            person=person,
            style=style,
            timestamp__lte=self.context['date']
        ).first()

        if not score:
            return None
        
        return score.value
    
    def get_problematic(self, obj):
        # obj is person
        return self.get_style_score(obj, 'problematic')
    
    def get_simple(self, obj):
        # obj is person
        return self.get_style_score(obj, 'simple')
    
    def get_sophisticated(self, obj):
        # obj is person
        return self.get_style_score(obj, 'sophisticated')

    problematic = serializers.SerializerMethodField()
    simple = serializers.SerializerMethodField()
    sophisticated = serializers.SerializerMethodField()
