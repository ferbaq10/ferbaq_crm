from rest_framework import serializers

from catalog.serializers import CitySerializer, BusinessGroupSerializer
from client.models import Client


class ClientSerializer(serializers.ModelSerializer):
    city = CitySerializer()
    business_group = BusinessGroupSerializer()

    # Campos de timestamp heredados de TimeStampedModel
    created = serializers.DateTimeField(read_only=True)
    modified = serializers.DateTimeField(read_only=True)

    # Campo de soft delete heredado de SoftDeletableModel
    is_removed = serializers.BooleanField(required=False)

    class Meta:
        model = Client
        fields = [
            'id',
            'rfc',
            'company',
            'id_client',
            'city',
            'business_group',
            'created',
            'modified',
            'is_removed'
        ]

    def to_representation(self, instance):
        """
        Personalizar la representación de salida
        """
        representation = super().to_representation(instance)

        # Formatear fechas si es necesario
        if representation.get('created'):
            representation['created'] = instance.created.strftime('%Y-%m-%d %H:%M')
        if representation.get('modified'):
            representation['modified'] = instance.modified.strftime('%Y-%m-%d %H:%M')

        return representation

class ClientWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = [
            'id',
            'rfc',
            'company',
            'id_client',
            'city',
            'business_group',
            'is_removed'
        ]

        extra_kwargs = {
            'rfc': {
                'required': True,
                'help_text': 'RFC único del cliente'
            },
            'company': {
                'required': True,
                'help_text': 'Razón social única del cliente'
            },
            'id_client': {
                'required': True,
                'help_text': 'ID único del cliente'
            }
        }

    def validate_rfc(self, value):
        if not value:
            raise serializers.ValidationError("El RFC es requerido")
        if len(value) < 12 or len(value) > 13:
            raise serializers.ValidationError("El RFC debe tener entre 12 y 13 caracteres")
        return value.upper()

    def validate_company(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("La razón social es requerida")
        return value.strip()