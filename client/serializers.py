from rest_framework import serializers
from client.models import Client
from catalog.models import City, BusinessGroup
from contact.models import Contact

class ClientSerializer(serializers.ModelSerializer):
    rfc = serializers.CharField(
        max_length=20,
        required=True,
        error_messages={
            'required': 'El RFC es obligatorio.',
            'max_length': 'El RFC no puede tener más de 20 caracteres.'
        }
    )
    company = serializers.CharField(
        max_length=100,
        required=True,
        error_messages={
            'required': 'La razón social es obligatoria.',
            'max_length': 'La razón social no puede tener más de 100 caracteres.'
        }
    )
    city = serializers.PrimaryKeyRelatedField(
        queryset=City.objects.all(),
        required=False,
        allow_null=True
    )
    business_group = serializers.PrimaryKeyRelatedField(
        queryset=BusinessGroup.objects.all(),
        many=True,
        required=False
    )
    contact = serializers.PrimaryKeyRelatedField(
        queryset=Contact.objects.all(),
        many=True,
        required=False
    )

    class Meta:
        model = Client
        fields = '__all__'
