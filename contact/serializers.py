from rest_framework import serializers
from django.core.validators import RegexValidator, EmailValidator
from .models import ( Contact)
from catalog.models import City


class ContactSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=100, required=True,
                                 error_messages={
            'required': 'El campo nombre es obligatorio.',
            'max_length': 'El nombre no puede tener más de 100 caracteres.'
        })
    address = serializers.CharField(max_length=255, required=False, allow_null=True, allow_blank=True)
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
    phone = serializers.CharField(max_length=15, 
                                  required=False, allow_null=True, allow_blank=True,
                                  validators=[RegexValidator(regex=r'^\d{10,}$', 
                                                             message="El número debe tener al menos 12 dígitos")])
    city_id = serializers.PrimaryKeyRelatedField(queryset=City.objects.all(), required=False)

    # Campo de soft delete heredado de SoftDeletableModel
    is_removed = serializers.BooleanField()

    class Meta:
        model = Contact
        fields = '__all__'