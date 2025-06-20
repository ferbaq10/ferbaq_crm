from rest_framework import serializers
from .models import ActivityLog
from opportunity.serializers import OpportunitySerializer
from opportunity.models import Opportunity


class ActivityLogSerializer(serializers.ModelSerializer):
    opportunity = OpportunitySerializer(read_only=True)

    class Meta:
        model = ActivityLog
        fields = [
            'id',
            'name',
            'longitude',
            'latitude',
            'opportunity',
            'is_removed',
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

    name = serializers.CharField(
        required=True,
        max_length=100,
        error_messages={
            'required': 'El nombre es obligatorio.',
            'max_length': 'El nombre no puede tener más de 100 caracteres.',
            'blank': 'El nombre no puede estar vacío.',
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

    class Meta:
        model = ActivityLog
        fields = [
            'id',
            'name',
            'longitude',
            'latitude',
            'opportunity',
            'is_removed',
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
