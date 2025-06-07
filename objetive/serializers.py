from rest_framework import serializers
from objetive.models import Objetive
from catalog.models import Period
from django.contrib.auth import get_user_model

User = get_user_model()

class ObjetiveSerializer(serializers.ModelSerializer):
    name = serializers.CharField(
        max_length=100,
        required=True,
        error_messages={
            'required': 'El nombre del objetivo es obligatorio.',
            'max_length': 'El nombre no puede tener más de 100 caracteres.'
        }
    )
    amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        required=True,
        error_messages={
            'required': 'El monto es obligatorio.',
            'invalid': 'El monto debe ser un número decimal válido.'
        }
    )
    period = serializers.PrimaryKeyRelatedField(
        queryset=Period.objects.all(),
        required=False,
        allow_null=True
    )
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=False,
        allow_null=True
    )

    class Meta:
        model = Objetive
        fields = '__all__'