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

from rest_framework import serializers
from catalog.serializers import CitySerializer, BusinessGroupSerializer
from .models import Client
from catalog.models import City, BusinessGroup

from rest_framework import serializers
from .models import Client, City, BusinessGroup
from catalog.serializers import CitySerializer, BusinessGroupSerializer

class ClientWriteSerializer(serializers.ModelSerializer):
    # Entrada: solo IDs
    city = serializers.PrimaryKeyRelatedField(queryset=City.objects.all(), write_only=True)
    business_group = serializers.PrimaryKeyRelatedField(queryset=BusinessGroup.objects.all(), write_only=True)

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
        Sobrescribe to_representation para devolver el objeto City completo
        cuando el serializador se usa para lectura (e.g., GET).
        """
        # Primero, obtenemos la representación por defecto del serializador.
        # Esto incluye el 'id' de la ciudad porque 'city' es un PrimaryKeyRelatedField.
        ret = super().to_representation(instance)

        # Ahora, si 'city' existe en la instancia (es decir, el cliente tiene una ciudad asociada),
        # usamos el CitySerializer para obtener la representación completa del objeto City.
        if instance.city:
            ret['city'] = CitySerializer(instance.city).data
        else:
            ret['city'] = None # Si no hay ciudad, establece el campo como None

        if instance.business_group:
            ret['business_group'] = CitySerializer(instance.business_group).data
        else:
            ret['business_group'] = None # Si no hay business group, establece el campo como None

        return ret
