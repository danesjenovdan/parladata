from rest_framework.serializers import Serializer, IntegerField, DateTimeField

class CardSerializer(Serializer):
    id = IntegerField()
    created_at = DateTimeField()
    updated_at = DateTimeField()

    def get_fields(self, *args, **kwargs):
        fields = super().get_fields(*args, **kwargs)
        for field in fields:
            fields[field].read_only = True
        return fields
