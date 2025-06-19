from rest_framework import serializers
from objetive.models import Objetive
from django.contrib.auth import get_user_model

User = get_user_model()


class ObjetiveSerializer(serializers.ModelSerializer):
    currency = serializers.StringRelatedField()
    period = serializers.StringRelatedField()
    user = serializers.StringRelatedField()

    class Meta:
        model = Objetive
        fields = '__all__'


class ObjetiveWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Objetive
        fields = ['name', 'amount', 'currency', 'period', 'user']
        extra_kwargs = {
            'name': {
                'required': True,
                'error_messages': {
                    'required': 'El nombre es obligatorio.',
                    'unique': 'Este nombre de objetivo ya existe.',
                    'max_length': 'El nombre no puede exceder 100 caracteres.'
                }
            },
            'amount': {
                'required': True,
                'error_messages': {
                    'required': 'El monto es obligatorio.',
                    'invalid': 'Debe ser un número válido.'
                }
            },
            'currency': {
                'error_messages': {
                    'invalid': 'Debe seleccionar una moneda válida.'
                }
            },
            'period': {
                'error_messages': {
                    'invalid': 'Debe seleccionar un período válido.'
                }
            },
            'user': {
                'error_messages': {
                    'invalid': 'Debe seleccionar un usuario válido.'
                }
            }
        }

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("El monto debe ser mayor a cero.")
        return value
