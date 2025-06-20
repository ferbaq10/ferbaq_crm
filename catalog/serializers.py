from rest_framework import serializers
from catalog.models import (
    UDN, WorkCell, BusinessGroup, Division, Subdivision, Specialty,
    ProjectStatus, City, Period, StatusOpportunity, Currency, Job, OpportunityType
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


class WorkCellSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=100, required=True,
                                 error_messages={
            'required': 'El campo nombre es obligatorio.',
            'max_length': 'El nombre no puede tener más de 100 caracteres.'
        })
    udn = serializers.PrimaryKeyRelatedField(queryset=UDN.objects.all(), required=True)

    class Meta:
        model = WorkCell
        fields = [
            'id',
            'name',
            'udn',
            'is_removed'
        ]


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


class DivisionSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=100, required=True,
                                 error_messages={
            'required': 'El campo nombre es obligatorio.',
            'max_length': 'El nombre no puede tener más de 100 caracteres.'
        })
    business_group = serializers.PrimaryKeyRelatedField(queryset=BusinessGroup.objects.all(), required=True,
                                                        error_messages={
            'required': 'El campo nombre es obligatorio.',
        })

    class Meta:
        model = Division
        fields = [
            'id',
            'name',
            'business_group',
            'is_removed',
        ]


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