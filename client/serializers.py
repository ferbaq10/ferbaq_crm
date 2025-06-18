from rest_framework import serializers

from catalog.serializers import CitySerializer, BusinessGroupSerializer
from .models import Client, City, BusinessGroup


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
            'city',
            'company',
            'id_client',
            'is_removed',
            'business_group'
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
    # Entrada: solo IDs
    city = serializers.PrimaryKeyRelatedField(queryset=City.objects.all(), write_only=True)
    business_group = serializers.PrimaryKeyRelatedField(queryset=BusinessGroup.objects.all(), write_only=True)

    class Meta:
        model = Client
        fields = [
            'id',
            'rfc',
            'city',
            'company',
            'id_client',
            'is_removed',
            'business_group'
        ]

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

    def to_representation(self, instance):
        """
            Sobrescribe to_representation para devolver city y business_group como objetos completos.
        """
        ret = super().to_representation(instance)

        ret['city'] = CitySerializer(instance.city).data if instance.city else None

        ret['business_group'] = BusinessGroupSerializer(instance.business_group).data \
            if instance.business_group else None

        return ret
