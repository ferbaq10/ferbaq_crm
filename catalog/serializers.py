from rest_framework import serializers
from catalog.models import (
    UDN, WorkCell, BusinessGroup, Division, Subdivision, Specialty,
    ProjectStatus, City, Period, StatusOpportunity, Currency, Job, OpportunityType,
    MeetingType, MeetingResult, LostOpportunityType, PurchaseStatusType
)

class UDNSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=100, required=True,
                                 error_messages={
            'required': 'El campo nombre es obligatorio.',
            'max_length': 'El nombre no puede tener más de 100 caracteres.'
        })

    class Meta:
        model = UDN
        fields = [
            'id',
            'name',
            'is_removed',
        ]
        read_only_fields = ['created', 'modified']


class WorkCellSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=100, required=True,
                                 error_messages={
            'required': 'El campo nombre es obligatorio.',
            'max_length': 'El nombre no puede tener más de 100 caracteres.'
        })
    udn = UDNSerializer()

    class Meta:
        model = WorkCell
        fields = [
            'id',
            'name',
            'udn',
            'is_removed'
        ]
        read_only_fields = ['created', 'modified']

class WorkCellWriteSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=100, required=True,
                                 error_messages={
            'required': 'El campo nombre es obligatorio.',
            'max_length': 'El nombre no puede tener más de 100 caracteres.'
        })
    udn = serializers.PrimaryKeyRelatedField(
        queryset=UDN.objects.all(),
        required=False,
        allow_null=True
    )

    class Meta:
        model = WorkCell
        fields = [
            'id',
            'name',
            'udn',
            'is_removed'
        ]
        read_only_fields = ['created', 'modified']

    def to_representation(self, instance):
        """Personalizar la representación de salida"""
        data = super().to_representation(instance)

        # Convertir udn de ID a objeto completo
        if instance.udn:
            data['udn'] = {
                'id': instance.udn.id,
                'name': instance.udn.name,
                'is_removed': instance.udn.is_removed
            }
        else:
            data['udn'] = None

        return data


class BusinessGroupSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=100, required=True,
                                 error_messages={
            'required': 'El campo nombre es obligatorio.',
            'max_length': 'El nombre no puede tener más de 100 caracteres.'
        })

    class Meta:
        model = BusinessGroup
        fields = [
            'id',
            'name',
            'is_removed',
        ]
        read_only_fields = ['created', 'modified']


class DivisionSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=100, required=True,
                                 error_messages={
            'required': 'El campo nombre es obligatorio.',
            'max_length': 'El nombre no puede tener más de 100 caracteres.'
        })

    class Meta:
        model = Division
        fields = [
            'id',
            'name',
            'is_removed',
        ]
        read_only_fields = ['created', 'modified']


class SubdivisionSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=100, required=True,
                                 error_messages={
            'required': 'El campo nombre es obligatorio.',
            'max_length': 'El nombre no puede tener más de 100 caracteres.'
        })
    division = serializers.PrimaryKeyRelatedField(queryset=Division.objects.all(), required=True,
                                                  error_messages={
            'required': 'El campo nombre es obligatorio.',
        })

    class Meta:
        model = Subdivision
        fields = [
            'id',
            'name',
            'division',
            'is_removed',
        ]
        read_only_fields = ['created', 'modified']


class SpecialtySerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=100, required=True,
                                 error_messages={
            'required': 'El campo nombre es obligatorio.',
            'max_length': 'El nombre no puede tener más de 100 caracteres.'
        })

    class Meta:
        model = Specialty
        fields = [
            'id',
            'name',
            'is_removed',
        ]
        read_only_fields = ['created', 'modified']


class ProjectStatusSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=100, required=True,
                                 error_messages={
            'required': 'El campo nombre es obligatorio.',
            'max_length': 'El nombre no puede tener más de 100 caracteres.'
        })

    class Meta:
        model = ProjectStatus
        fields = [
            'id',
            'name',
            'is_removed',
        ]
        read_only_fields = ['created', 'modified']


class CitySerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=100, required=True,
                                 error_messages={
            'required': 'El campo nombre es obligatorio.',
            'max_length': 'El nombre no puede tener más de 100 caracteres.'
        })

    class Meta:
        model = City
        fields = [
            'id',
            'name',
            'is_removed',
        ]
        read_only_fields = ['created', 'modified']


class PeriodSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=100, required=True,
                                 error_messages={
            'required': 'El campo nombre es obligatorio.',
            'max_length': 'El nombre no puede tener más de 100 caracteres.'
        })

    class Meta:
        model = Period
        fields = [
            'id',
            'name',
            'is_removed',
        ]
        read_only_fields = ['created', 'modified']


class StatusOpportunitySerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=100, required=True,
                                 error_messages={
            'required': 'El campo nombre es obligatorio.',
            'max_length': 'El nombre no puede tener más de 100 caracteres.'
        })

    class Meta:
        model = StatusOpportunity
        fields = [
            'id',
            'name',
            'is_removed',
        ]
        read_only_fields = ['created', 'modified']


class CurrencySerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=100, required=True,
                                 error_messages={
            'required': 'El campo nombre es obligatorio.',
            'max_length': 'El nombre no puede tener más de 100 caracteres.'
        })

    class Meta:
        model = Currency
        fields = [
            'id',
            'name',
            'is_removed',
        ]
        read_only_fields = ['created', 'modified']


class JobSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=100, required=True,
                                 error_messages={
                                     'required': 'El campo nombre es obligatorio.',
                                     'max_length': 'El nombre no puede tener más de 100 caracteres.'
                                 })

    class Meta:
        model = Job
        fields = [
            'id',
            'name',
            'is_removed',
        ]
        read_only_fields = ['created', 'modified']


class OpportunityTypeSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=100, required=True,
                                 error_messages={
            'required': 'El campo nombre es obligatorio.',
            'max_length': 'El nombre no puede tener más de 100 caracteres.'
        })

    class Meta:
        model = OpportunityType
        fields = [
            'id',
            'name',
            'is_removed',
        ]
        read_only_fields = ['created', 'modified']


class MeetingTypeSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=100, required=True,
                                 error_messages={
            'required': 'El campo nombre es obligatorio.',
            'max_length': 'El nombre no puede tener más de 100 caracteres.'
        })

    class Meta:
        model = MeetingType
        fields = [
            'id',
            'name',
            'is_removed',
        ]
        read_only_fields = ['created', 'modified']


class MeetingResultSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=100, required=True,
                                 error_messages={
            'required': 'El campo nombre es obligatorio.',
            'max_length': 'El nombre no puede tener más de 100 caracteres.'
        })

    class Meta:
        model = MeetingResult
        fields = [
            'id',
            'name',
            'is_removed',
        ]
        read_only_fields = ['created', 'modified']


class LostOpportunityTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LostOpportunityType
        fields = [
            'id',
            'name',
            'is_removed',
        ]
        read_only_fields = ['created', 'modified']


class PurchaseStatusTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseStatusType
        fields = [
            'id',
            'name',
            'is_removed',
        ]
        read_only_fields = ['created', 'modified']