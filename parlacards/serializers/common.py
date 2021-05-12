from rest_framework import serializers

class CardSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()

    def get_fields(self, *args, **kwargs):
        fields = super().get_fields(*args, **kwargs)
        for field in fields:
            fields[field].read_only = True
        return fields

class VersionableSerializerField(serializers.Field):
    def __init__(self, property_model_name, **kwargs):
        self.property_model_name = property_model_name
        kwargs['source'] = '*'
        kwargs['read_only'] = True
        super().__init__(**kwargs)
    
    def to_representation(self, value):
        if 'date' not in self.context.keys():
            raise Exception(f'You need to provide date in the serializer context.')

        object_to_serialize = value
        return object_to_serialize.versionable_property_on_date(
            owner=object_to_serialize,
            property_model_name=self.property_model_name,
            datetime=self.context['date'],
        )


class CommonPersonSerializer(CardSerializer):
    def get_party(self, obj):
        active_parliamentary_group_membership = obj.parliamentary_group_on_date(self.context['date'])
        if not active_parliamentary_group_membership:
            return None

        serializer = CommonOrganizationSerializer(obj.parliamentary_group_on_date(self.context['date']), context=self.context)
        return serializer.data
    
    slug = serializers.CharField()
    name = VersionableSerializerField(property_model_name='PersonName')
    honorific_prefix = VersionableSerializerField(property_model_name='PersonHonorificPrefix')
    honorific_suffix = VersionableSerializerField(property_model_name='PersonHonorificSuffix')
    preferred_pronoun = VersionableSerializerField(property_model_name='PersonPreferredPronoun')
    party = serializers.SerializerMethodField()


class CommonOrganizationSerializer(CardSerializer):
    name = VersionableSerializerField(property_model_name='OrganizationName')
    acronym = VersionableSerializerField(property_model_name='OrganizationAcronym')
    email = serializers.CharField()
    slug = serializers.CharField()
