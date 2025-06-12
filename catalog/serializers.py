from rest_framework import serializers
from catalog.models import (
    UDN, WorkCell, BusinessGroup, Division, Subdivision, Specialty,
    ProjectStatus, City, Period, StatusOpportunity, Currency
)

class UDNSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=100, required=True,
                                 error_messages={
            'required': 'El campo nombre es obligatorio.',
            'max_length': 'El nombre no puede tener más de 100 caracteres.'
        })

    class Meta:
        model = UDN
        fields = '__all__'


class WorkCellSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=100, required=True,
                                 error_messages={
            'required': 'El campo nombre es obligatorio.',
            'max_length': 'El nombre no puede tener más de 100 caracteres.'
        })
    udn = serializers.PrimaryKeyRelatedField(queryset=UDN.objects.all(), required=True)

    class Meta:
        model = WorkCell
        fields = '__all__'


class BusinessGroupSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=100, required=True,
                                 error_messages={
            'required': 'El campo nombre es obligatorio.',
            'max_length': 'El nombre no puede tener más de 100 caracteres.'
        })

    class Meta:
        model = BusinessGroup
        fields = '__all__'


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
        fields = '__all__'


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
        fields = '__all__'


class SpecialtySerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=100, required=True,
                                 error_messages={
            'required': 'El campo nombre es obligatorio.',
            'max_length': 'El nombre no puede tener más de 100 caracteres.'
        })

    class Meta:
        model = Specialty
        fields = '__all__'


class ProjectStatusSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=100, required=True,
                                 error_messages={
            'required': 'El campo nombre es obligatorio.',
            'max_length': 'El nombre no puede tener más de 100 caracteres.'
        })

    class Meta:
        model = ProjectStatus
        fields = '__all__'


class CitySerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=100, required=True,
                                 error_messages={
            'required': 'El campo nombre es obligatorio.',
            'max_length': 'El nombre no puede tener más de 100 caracteres.'
        })

    class Meta:
        model = City
        fields = '__all__'


class PeriodSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=100, required=True,
                                 error_messages={
            'required': 'El campo nombre es obligatorio.',
            'max_length': 'El nombre no puede tener más de 100 caracteres.'
        })

    class Meta:
        model = Period
        fields = '__all__'


class StatusOpportunitySerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=100, required=True,
                                 error_messages={
            'required': 'El campo nombre es obligatorio.',
            'max_length': 'El nombre no puede tener más de 100 caracteres.'
        })

    class Meta:
        model = StatusOpportunity
        fields = '__all__'


class CurrencySerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=100, required=True,
                                 error_messages={
            'required': 'El campo nombre es obligatorio.',
            'max_length': 'El nombre no puede tener más de 100 caracteres.'
        })

    class Meta:
        model = Currency
        fields = '__all__'