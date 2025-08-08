from django.core.validators import RegexValidator, EmailValidator
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from catalog.models import Job
from catalog.serializers import JobSerializer
from client.models import Client
from client.serializers import ClientSerializer
from .models import Contact


class ContactSerializer(serializers.ModelSerializer):
    job = JobSerializer(read_only=True)
    clients = ClientSerializer(
        many=True,
        read_only=True,
        source='contact_pref_clients', # atributo cargado por Prefetch
    )

    class Meta:
        model = Contact
        fields = [
            'id',
            'job',
            'name',
            'email',
            'phone',
            'address',
            'clients',
            'is_removed'
        ]
        read_only_fields = ['created', 'modified']

class ContactWriteSerializer(serializers.ModelSerializer):
    name = serializers.CharField(
        max_length=100,
        required=True,
        validators=[
            UniqueValidator(
                queryset=Contact.objects.all(),
                message="El nombre del contacto debe ser único."
            )
        ],
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
        required=False,
        validators=[EmailValidator(message="Debe ser un correo electrónico válido.")],
        error_messages={
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

    clients = serializers.PrimaryKeyRelatedField(
        queryset=Client.objects.all(),
        many=True,
        required=True,
        allow_empty=False,
        error_messages={
            'required': 'Debe seleccionar al menos un cliente.',
            'empty': 'Debe asociar al menos un cliente.',
            'invalid': 'El formato del listado de clientes es incorrecto.'
        }
    )

    job = serializers.PrimaryKeyRelatedField(
        queryset=Job.objects.all(),
        required=False,
        allow_null=True
    )

    class Meta:
        model = Contact
        fields = [
            'id',
            'job',
            'name',
            'phone',
            'email',
            'clients',
            'address',
            'is_removed'
        ]
        read_only_fields = ['created']


    def to_representation(self, instance):
        """
            Sobrescribe to_representation para devolver city y clients como objetos completos.
        """

        ret = super().to_representation(instance)

        ret['clients'] = ClientSerializer(instance.clients.all(), many=True).data if instance.clients else None

        ret['job'] = JobSerializer(instance.job).data if instance.job else None

        return ret
