from django.core.validators import RegexValidator, EmailValidator
from rest_framework import serializers

from catalog.models import City, Job
from catalog.serializers import CitySerializer, JobSerializer
from client.serializers import ClientSerializer
from .models import Contact
from client.models import Client

class ContactSerializer(serializers.ModelSerializer):
    city = CitySerializer(read_only=True)
    job = JobSerializer(read_only=True)
    clients = ClientSerializer(many=True, read_only=True)

    class Meta:
        model = Contact
        fields = [
            'id',
            'job',
            'name',
            'city',
            'phone',
            'email',
            'address',
            'clients',
            'is_removed'
        ]
        read_only_fields = fields  # marca todo como solo lectura


class ContactWriteSerializer(serializers.ModelSerializer):
    name = serializers.CharField(
        max_length=100,
        required=True,
        error_messages={
            'required': 'El campo nombre es obligatorio.',
            'max_length': 'El nombre no puede tener más de 100 caracteres.'
        }
    )
    address = serializers.CharField(
        max_length=255,
        required=False,
        allow_null=True,
        allow_blank=True
    )
    email = serializers.EmailField(
        max_length=100,
        required=True,
        validators=[EmailValidator(message="Debe ser un correo electrónico válido.")],
        error_messages={
            'required': 'El campo correo electrónico es obligatorio.',
            'max_length': 'El correo electrónico no puede tener más de 100 caracteres.',
            'invalid': 'Debe ingresar un correo electrónico válido.'
        }
    )
    phone = serializers.CharField(
        max_length=15,
        required=False,
        allow_null=True,
        allow_blank=True,
        validators=[RegexValidator(
            regex=r'^\d{10,}$',
            message="El número debe tener al menos 10 dígitos"
        )]
    )
    city = serializers.PrimaryKeyRelatedField(
        queryset=City.objects.all(),
        required=False
    )

    clients = serializers.PrimaryKeyRelatedField(
        queryset=Client.objects.all(),
        many=True,
        required=False
    )

    job = serializers.PrimaryKeyRelatedField(
        queryset=Job.objects.all(),
        required=False
    )

    class Meta:
        model = Contact
        fields = [
            'id',
            'job',
            'name',
            'city',
            'phone',
            'email',
            'clients',
            'address',
            'is_removed'
        ]

    def to_representation(self, instance):
        """
            Sobrescribe to_representation para devolver city y clients como objetos completos.
        """

        ret = super().to_representation(instance)

        ret['city'] = CitySerializer(instance.city).data if instance.city else None

        ret['clients'] = ClientSerializer(instance.clients.all(), many=True).data if instance.clients else None

        ret['job'] = JobSerializer(instance.job).data if instance.job else None

        return ret
