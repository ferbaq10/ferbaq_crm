from rest_framework import serializers
from client.models import Client


class ClientSerializer(serializers.ModelSerializer):
    # Campos de solo lectura para mostrar información relacionada
    city_name = serializers.CharField(source='city.name', read_only=True)
    business_group_name = serializers.CharField(source='business_group.name', read_only=True)

    # Campos de timestamp heredados de TimeStampedModel
    created = serializers.DateTimeField(read_only=True)
    modified = serializers.DateTimeField(read_only=True)

    # Campo de soft delete heredado de SoftDeletableModel
    is_removed = serializers.BooleanField(read_only=True)

    class Meta:
        model = Client
        fields = [
            'id',
            'rfc',
            'company',
            'id_client',
            'city',
            'city_name',
            'business_group',
            'business_group_name',
            'created',
            'modified',
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
        """
        Validación personalizada para RFC
        """
        if not value:
            raise serializers.ValidationError("El RFC es requerido")

        # Ejemplo de validación de formato RFC (ajusta según tus necesidades)
        if len(value) < 12 or len(value) > 13:
            raise serializers.ValidationError("El RFC debe tener entre 12 y 13 caracteres")

        return value.upper()

    def validate_company(self, value):
        """
        Validación personalizada para razón social
        """
        if not value or not value.strip():
            raise serializers.ValidationError("La razón social es requerida")

        return value.strip()

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
