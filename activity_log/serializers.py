from rest_framework import serializers

from catalog.models import MeetingType, MeetingResult
from catalog.serializers import MeetingTypeSerializer, MeetingResultSerializer
from contact.models import Contact
from contact.serializers import ContactSerializer
from opportunity.models import Opportunity, CommercialActivity
from opportunity.serializers import OpportunitySerializer, CommercialActivitySerializer
from project.models import Project
from project.serializers import ProjectSerializer
from .models import ActivityLog


class ActivityLogSerializer(serializers.ModelSerializer):
    project = ProjectSerializer(read_only=True)
    contact = ContactSerializer(read_only=True)
    opportunity = OpportunitySerializer(read_only=True)
    activity_type = CommercialActivitySerializer(read_only=True)
    meeting_type = MeetingTypeSerializer(read_only=True)
    meeting_result = MeetingResultSerializer(read_only=True)
    activity_date_string = serializers.SerializerMethodField()

    class Meta:
        model = ActivityLog
        fields = [
             'id',
            'project',
            'contact',
            'latitude',
            'longitude',
            'is_removed',
            'opportunity',
            'observation',
            'meeting_type',
            'activity_type',
            'activity_date',
            'meeting_result',
            'activity_date_string'
        ]
        read_only_fields = ['id', 'is_removed']

    def get_activity_date_string(self, obj):
        if obj.activity_date:
            return obj.activity_date.strftime("%d/%m/%Y %I:%M %p")  # Ej: 30/06/2025 10:48 AM
        return None


class ActivityLogWriteSerializer(serializers.ModelSerializer):
    activity_type = serializers.PrimaryKeyRelatedField(
        queryset=CommercialActivity.objects.all(),
        error_messages={'required': 'La actividad comercial es obligatoria.'}
    )
    project = serializers.PrimaryKeyRelatedField(
        queryset=Project.objects.all(),
        error_messages={'required': 'El proyecto es obligatorio.'}
    )
    contact = serializers.PrimaryKeyRelatedField(
        queryset=Contact.objects.all(),
        error_messages={'required': 'El contacto es obligatorio.'}
    )
    meeting_type = serializers.PrimaryKeyRelatedField(
        queryset=MeetingType.objects.all(),
        error_messages={'required': 'El tipo de reunión es obligatorio.'}
    )
    meeting_result = serializers.PrimaryKeyRelatedField(
        queryset=MeetingResult.objects.all(),
        error_messages={'required': 'El resultado de reunión es obligatorio.'}
    )
    opportunity = serializers.PrimaryKeyRelatedField(
        queryset=Opportunity.objects.all(),
        allow_null=True,
        required=False,
    )

    class Meta:
        model = ActivityLog
        fields = [
            'id',
            'project',
            'contact',
            'latitude',
            'longitude',
            'is_removed',
            'opportunity',
            'observation',
            'activity_date',
            'activity_type',
            'meeting_type',
            'meeting_result',
        ]
        read_only_fields = ['id']

    def validate(self, data):
        lat = data.get('latitude')
        lng = data.get('longitude')
        activity_date = data.get('activity_date')

        print("REQUEST DATA:", self.initial_data)
        print("SERIALIZED DATA:", data)

        if (lat is not None and lng is None) or (lng is not None and lat is None):
            raise serializers.ValidationError({
                'non_field_errors': ["Si proporcionas latitud, también debes proporcionar longitud, y viceversa."]
            })

        if isinstance(activity_date, str):
            raise serializers.ValidationError({
                'activity_date': ["La fecha de actividad debe ser un objeto datetime, no una cadena."]
            })

        return data

    def to_representation(self, instance):
        """Devuelve la representación con objetos anidados aunque sea un serializer de escritura"""
        ret = super().to_representation(instance)
        ret['contact'] = ContactSerializer(instance.contact).data if instance.contact else None
        ret['project'] = ProjectSerializer(instance.project).data if instance.project else None
        ret['activity_type'] = CommercialActivitySerializer(instance.activity_type).data if instance.activity_type else None
        ret['meeting_type'] = MeetingTypeSerializer(instance.meeting_type).data if instance.meeting_type else None
        ret['meeting_result'] = MeetingResultSerializer(instance.meeting_result).data if instance.meeting_result else None
        return ret



