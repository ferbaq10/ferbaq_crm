from rest_framework import serializers
from .models import Project

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'
        extra_kwargs = {
            'latitude': {
                'required': False,
                'error_messages': {
                    'invalid': 'Ingrese una latitud válida.',
                }
            },
            'longitude': {
                'required': False,
                'error_messages': {
                    'invalid': 'Ingrese una longitud válida.',
                }
            },
            'description': {
                'required': False,
                'error_messages': {
                    'blank': 'La descripción no puede estar vacía.',
                }
            }
        }

    def validate_latitude(self, value):
        if value is not None and (value < -90 or value > 90):
            raise serializers.ValidationError("La latitud debe estar entre -90 y 90 grados.")
        return value

    def validate_longitude(self, value):
        if value is not None and (value < -180 or value > 180):
            raise serializers.ValidationError("La longitud debe estar entre -180 y 180 grados.")
        return value

    def validate_description(self, value):
        if value and len(value.strip()) < 10:
            raise serializers.ValidationError("La descripción debe tener al menos 10 caracteres.")
        return value
