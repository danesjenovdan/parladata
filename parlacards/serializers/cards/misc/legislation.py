from django.db.models import Q
from parlacards.pagination import create_paginator
from parlacards.serializers.common import CardSerializer, MandateSerializer
from parlacards.serializers.legislation import LegislationSerializer
from parladata.models.legislation import Law, LegislationClassification


class LegislationMixin:
    def _get_legislation(self, params, mandate=None, session=None):
        text_filter = params.get("text", "")
        order = params.get("order_by", "-timestamp")
        classification_filter = params.get("classification", None)

        legislation = Law.objects.filter(
            Q(timestamp__lte=self.context["request_date"]) | Q(timestamp__isnull=True),
            text__icontains=text_filter,
        )

        if mandate:
            legislation = legislation.filter(mandate=mandate)
        if session:
            legislation = legislation.filter(legislationconsideration__session=session)

        legislation = legislation.distinct("id")

        if classification_filter:
            classifications = classification_filter.split(",")
            legislation = legislation.filter(classification__name__in=classifications)

        # needs to be a new query because distinct and order_by need the same field as first param
        legislation = Law.objects.filter(id__in=legislation).order_by(order, "id")

        return legislation

    def _get_classifications(self):
        return (
            LegislationClassification.objects.all()
            .distinct("name")
            .values_list("name", flat=True)
        )


class LegislationCardSerializer(CardSerializer, LegislationMixin):
    def get_results(self, mandate):
        # this is implemented in to_representation for pagination
        return None

    def get_mandate(self, mandate):
        serializer = MandateSerializer(mandate, context=self.context)
        return serializer.data

    def to_representation(self, mandate):
        parent_data = super().to_representation(mandate)

        legislation = self._get_legislation(
            self.context.get("GET", {}), mandate=mandate
        )

        paged_object_list, pagination_metadata = create_paginator(
            self.context.get("GET", {}), legislation, prefix="legislation:"
        )

        legislation_serializer = LegislationSerializer(
            paged_object_list, many=True, context=self.context
        )

        # TODO standardize this and more importantly, cache it!
        classifications = self._get_classifications()

        return {
            **parent_data,
            **pagination_metadata,
            "results": {
                "legislation": legislation_serializer.data,
                "classifications": classifications,
            },
        }
