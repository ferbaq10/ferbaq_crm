from rest_framework import serializers

from catalog.serializers import MeetingTypeSerializer, MeetingResultSerializer
from catalog.models import MeetingType, MeetingResult
from project.serializers import ProjectSerializer
from .models import ActivityLog
from opportunity.serializers import OpportunitySerializer, CommercialActivitySerializer
from opportunity.models import Opportunity, CommercialActivity


class ActivityLogSerializer(serializers.ModelSerializer):
    opportunity = OpportunitySerializer(read_only=True)
    activity_type = CommercialActivitySerializer(read_only=True)
    meeting_type = MeetingTypeSerializer(read_only=True)
    meeting_result = MeetingResultSerializer(read_only=True)
    project = ProjectSerializer(read_only=True)


    class Meta:
        model = ActivityLog
        fields = [
             'id',
            'project',
            'latitude',
            'longitude',
            'is_removed',
            'opportunity',
            'observation',
            'meeting_type',
            'activity_type',
            'activity_date',
            'meeting_result',
        ]
        read_only_fields = ['id', 'is_removed']


class ActivityLogWriteSerializer(serializers.ModelSerializer):
    opportunity = serializers.PrimaryKeyRelatedField(
        queryset=Opportunity.objects.all(),
        required=False,
        allow_null=True,
        error_messages={
            'does_not_exist': 'La oportunidad seleccionada no existe.',
            'invalid': 'Formato inválido para la oportunidad.',
        }
    )
    activity_type = serializers.PrimaryKeyRelatedField(
        queryset=CommercialActivity.objects.all(),
        required=False,
        allow_null=True,
        error_messages={
            'does_not_exist': 'La actividad comercial seleccionada no existe.',
            'invalid': 'Formato inválido para la actividad comercial.',
        }
    )

    latitude = serializers.DecimalField(
        max_digits=9,
        decimal_places=6,
        required=False,
        allow_null=True,
        error_messages={
            'invalid': 'Latitud inválida.',
        }
    )

    longitude = serializers.DecimalField(
        max_digits=9,
        decimal_places=6,
        required=False,
        allow_null=True,
        error_messages={
            'invalid': 'Longitud inválida.',
        }
    )
    meeting_type = serializers.PrimaryKeyRelatedField(
        queryset=MeetingType.objects.all(),
        required=False,
        allow_null=True,
        error_messages={
            'does_not_exist': 'El tipo de reunión seleccionado no existe.',
            'invalid': 'Formato inválido para el tipo de reunión.',
        }
    )

    meeting_result = serializers.PrimaryKeyRelatedField(
        queryset=MeetingResult.objects.all(),
        required=False,
        allow_null=True,
        error_messages={
            'does_not_exist': 'El resultado de reunión seleccionado no existe.',
            'invalid': 'Formato inválido para el resultado de reunión.',
        }
    )

    class Meta:
        model = ActivityLog
        fields = [
            'id',
            'project',
            'latitude',
            'longitude',
            'is_removed',
            'opportunity',
            'observation',
            'meeting_type',
            'activity_type',
            'activity_date',
            'meeting_result',
        ]
        read_only_fields = ['id', 'is_removed']

    def validate(self, data):
        lat = data.get('latitude')
        lng = data.get('longitude')

        if (lat is not None and lng is None) or (lng is not None and lat is None):
            raise serializers.ValidationError("Si proporcionas latitud, también debes proporcionar longitud, y viceversa.")

        return data

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['opportunity'] = OpportunitySerializer(instance.opportunity).data if instance.opportunity else None
        return ret
