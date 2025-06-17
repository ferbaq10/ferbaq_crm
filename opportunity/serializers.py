from rest_framework import serializers
from .models import Opportunity, CommercialActivity
from django.core.validators import EmailValidator

class OpportunitySerializer(serializers.ModelSerializer):
    name = serializers.CharField(
        max_length=100,
        required=True,
        error_messages={
            'required': 'El nombre es obligatorio.',
            'max_length': 'El nombre no puede exceder los 100 caracteres.',
            'unique': 'Ya existe una oportunidad con este nombre.'
        }
    )
    email = serializers.EmailField(
        max_length=100,
        required=False,
        allow_null=True,
        allow_blank=True,
        validators=[EmailValidator(message="Debe ser un correo electrónico válido")],
        error_messages={
            'max_length': 'El correo no puede exceder los 100 caracteres.',
            'unique': 'Ya existe una oportunidad con este correo.'
        }
    )
    phone = serializers.IntegerField(
        required=False,
        allow_null=True,
        error_messages={
            'invalid': 'El número telefónico debe ser numérico.'
        }
    )
    amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        error_messages={
            'invalid': 'El monto debe ser un número decimal válido.'
        }
    )

    class Meta:
        model = Opportunity
        fields = '__all__'


class ComercialActivitySerializer(serializers.ModelSerializer):
    name = serializers.CharField(
        max_length=100,
        required=True,
        error_messages={
            'required': 'El nombre es obligatorio.',
            'max_length': 'El nombre no puede exceder los 100 caracteres.',
            'unique': 'Ya existe una actividad con este nombre.'
        }
    )

    # Campo de soft delete heredado de SoftDeletableModel
    is_removed = serializers.BooleanField()

    class Meta:
        model = CommercialActivity
        fields = '__all__'