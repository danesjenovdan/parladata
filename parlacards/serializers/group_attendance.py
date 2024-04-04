from parlacards.serializers.common import CommonSerializer, CommonOrganizationSerializer
from parlacards.models import SessionGroupAttendance

from rest_framework import serializers


class SessionGroupAttendanceSerializer(CommonSerializer):
    value = serializers.FloatField()
    group = CommonOrganizationSerializer()
