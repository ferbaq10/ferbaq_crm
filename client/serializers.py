from rest_framework import serializers

from catalog.serializers import CitySerializer, BusinessGroupSerializer
from .models import Client, City, BusinessGroup


class ClientSerializer(serializers.ModelSerializer):
    city = CitySerializer()
    business_group = BusinessGroupSerializer()

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
        read_only_fields = ['created', 'modified']

    # def to_representation(self, instance):
    #     # Forzar uso de select_related ya que DRF no lo hace automáticamente
    #     instance = Client.objects.select_related('city', 'business_group').get(pk=instance.pk)
    #     return super().to_representation(instance)


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
        read_only_fields = ['created']


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
