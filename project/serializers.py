from rest_framework import serializers

from catalog.models import Specialty, ProjectStatus, Subdivision, WorkCell
from catalog.serializers import BusinessGroupSerializer, SpecialtySerializer, SubdivisionSerializer, \
    ProjectStatusSerializer, WorkCellSerializer
from client.serializers import ClientSerializer
from .models import Client
from .models import Project


class ProjectSerializer(serializers.ModelSerializer):
    client = ClientSerializer()
    specialty = SpecialtySerializer()
    subdivision = SubdivisionSerializer()
    project_status = ProjectStatusSerializer()
    work_cell = WorkCellSerializer()

    # Campo de soft delete heredado de SoftDeletableModel
    is_removed = serializers.BooleanField(required=False)
   
    class Meta:
        model = Project
        fields = [
            'id',
            'name',
            'client',
            'latitude',
            'work_cell',
            'longitude',
            'specialty',
            'is_removed',
            'subdivision',
            'description',
            'project_status',
        ]

        read_only_fields = fields


class ProjectWriteSerializer(serializers.ModelSerializer):
    client = serializers.PrimaryKeyRelatedField(queryset=Client.objects.all())
    specialty = serializers.PrimaryKeyRelatedField(queryset=Specialty.objects.all(), required=False, allow_null=True)
    subdivision = serializers.PrimaryKeyRelatedField(queryset=Subdivision.objects.all())
    project_status = serializers.PrimaryKeyRelatedField(queryset=ProjectStatus.objects.all())
    work_cell = serializers.PrimaryKeyRelatedField(queryset=WorkCell.objects.all())

    class Meta:
        model = Project
        fields = [
            'id',
            'name',
            'client',
            'latitude',
            'longitude',
            'specialty',
            'subdivision',
            'description',
            'project_status',
            'work_cell',
            'is_removed',
        ]
        extra_kwargs = {
            'name': {
                'required': True,
                'error_messages': {
                    'required': 'El nombre es obligatorio.',
                    'blank': 'El nombre no puede estar vacío.'
                }
            },
            'latitude': {
                'required': False,
                'error_messages': {
                    'invalid': 'Ingrese una latitud válida.'
                }
            },
            'longitude': {
                'required': False,
                'error_messages': {
                    'invalid': 'Ingrese una longitud válida.'
                }
            },
            'description': {
                'required': False,
                'allow_blank': True,
                'error_messages': {
                    'blank': 'La descripción no puede estar vacía.'
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

    def to_representation(self, instance):
        """Devuelve la representación con objetos anidados aunque sea un serializer de escritura"""
        ret = super().to_representation(instance)
        ret['client'] = ClientSerializer(instance.client).data if instance.client else None
        ret['specialty'] = SpecialtySerializer(instance.specialty).data if instance.specialty else None
        ret['subdivision'] = SubdivisionSerializer(instance.subdivision).data if instance.subdivision else None
        ret['project_status'] = ProjectStatusSerializer(instance.project_status).data if instance.project_status else None
        ret['work_cell'] = WorkCellSerializer(instance.work_cell).data if instance.work_cell else None

        return ret

