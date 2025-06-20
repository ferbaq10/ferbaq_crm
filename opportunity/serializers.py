from datetime import datetime

from django.contrib.auth import get_user_model
from rest_framework import serializers

from catalog.models import OpportunityType, StatusOpportunity, Currency
from catalog.serializers import StatusOpportunitySerializer, CurrencySerializer, OpportunityTypeSerializer
from contact.models import Contact
from contact.serializers import ContactSerializer
from project.models import Project
from project.serializers import ProjectSerializer
from .models import CommercialActivity, FinanceOpportunity, Opportunity

User = get_user_model()


class FinanceOpportunitySerializer(serializers.ModelSerializer):
    name = serializers.CharField(
        max_length=100,
        required=True,
        error_messages={
            'required': 'El nombre es obligatorio.',
            'max_length': 'El nombre no puede exceder los 100 caracteres.',
            'unique': 'Ya existe un dato financiero con este nombre.'
        }
    )

    class Meta:
        model = FinanceOpportunity
        fields = [
            'id',
            'name',
            'is_removed',
            'opportunity',
            'earned_amount',
            'cost_subtotal',
            'offer_subtotal',
            'order_closing_date',
        ]


class CommercialActivitySerializer(serializers.ModelSerializer):
    name = serializers.CharField(
        max_length=100,
        required=True,
        error_messages={
            'required': 'El nombre es obligatorio.',
            'max_length': 'El nombre no puede exceder los 100 caracteres.',
            'unique': 'Ya existe una actividad con este nombre.'
        }
    )

    class Meta:
        model = CommercialActivity
        fields = [
            'id',
            'name',
            'is_removed',
        ]


# --- SOLO LECTURA ---
class OpportunitySerializer(serializers.ModelSerializer):
    contact = ContactSerializer()
    project = ProjectSerializer()
    currency = CurrencySerializer()
    opportunityType = OpportunityTypeSerializer()
    status_opportunity = StatusOpportunitySerializer()
    commercial_activity = CommercialActivitySerializer(many=True)

    finance_opportunities = FinanceOpportunitySerializer(
        source='financeopportunity_set',
        many=True,
        read_only=True
    )

    class Meta:
        model = Opportunity
        fields = [
            'name', 'description', 'amount', 'number_fvt',
            'date_reception', 'sent_date', 'date_status',
            'status_opportunity', 'contact', 'currency',
            'commercial_activity', 'agent', 'project', 'opportunityType',
            'finance_opportunities', 'is_removed'
        ]


# --- CREACIÓN / ACTUALIZACIÓN ---
class OpportunityWriteSerializer(serializers.ModelSerializer):
    project = serializers.PrimaryKeyRelatedField(queryset=Project.objects.all())
    contact = serializers.PrimaryKeyRelatedField(queryset=Contact.objects.all())
    currency = serializers.PrimaryKeyRelatedField(queryset=Currency.objects.all())
    commercial_activity = serializers.PrimaryKeyRelatedField(queryset=CommercialActivity.objects.all(), many=True)
    opportunityType = serializers.PrimaryKeyRelatedField(queryset=OpportunityType.objects.all())
    status_opportunity = serializers.PrimaryKeyRelatedField(queryset=StatusOpportunity.objects.all())

    finance_opportunities = FinanceOpportunitySerializer(
        source='financeopportunity_set',
        many=True,
        read_only=True
    )

    class Meta:
        model = Opportunity
        fields = [
            'name', 'description', 'amount', 'number_fvt',
            'date_reception', 'sent_date', 'date_status',
            'status_opportunity', 'contact', 'currency',
            'commercial_activity', 'agent', 'project', 'opportunityType',
            'finance_opportunities', 'is_removed',
        ]
        extra_kwargs = {
            'name': {'error_messages': {'unique': 'Ya existe una oportunidad con este nombre.'}},
            'number_fvt': {'error_messages': {'unique': 'Este formato de venta ya está registrado.'}},
            'amount': {'error_messages': {'required': 'El monto es obligatorio.'}},
            'status_opportunity': {'error_messages': {'required': 'El estado es obligatorio.'}},
            'contact': {'error_messages': {'required': 'El contacto es obligatorio.'}},
            'currency': {'error_messages': {'required': 'La moneda es obligatoria.'}},
            'agent': {'error_messages': {'required': 'El usuario asignado es obligatorio.'}},
            'project': {'error_messages': {'required': 'El proyecto es obligatorio.'}},
            'opportunityType': {'error_messages': {'required': 'El tipo de oportunidad es obligatorio.'}},
        }

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("El monto debe ser mayor a cero.")
        return value

    def validate(self, data):
        sent_date = data.get("sent_date")
        date_status = data.get("date_status")
        date_reception = data.get("date_reception")

        # Validar que sean datetime válidos
        if date_reception and not isinstance(date_reception, datetime):
            raise serializers.ValidationError(
                {"date_reception": "La fecha de recepción debe ser un valor datetime válido."})

        # Validar que sean datetime válidos
        if date_status and not isinstance(date_status, datetime):
            raise serializers.ValidationError(
                {"date_status": "La fecha del estado debe ser un valor datetime válido."})

        if sent_date and not isinstance(sent_date, datetime):
            raise serializers.ValidationError({"sent_date": "La fecha de envío debe ser un valor datetime válido."})


        if date_reception and sent_date and sent_date < date_reception:
            raise serializers.ValidationError("La fecha de envío no puede ser anterior a la de recepción.")
        return data

    def to_representation(self, instance):
        """Devuelve la representación con objetos anidados aunque sea un serializer de escritura"""
        ret = super().to_representation(instance)
        ret['contact'] = ContactSerializer(instance.contact).data if instance.contact else None
        ret['project'] = ProjectSerializer(instance.project).data if instance.project else None
        ret['currency'] = CurrencySerializer(instance.currency).data if instance.currency else None
        ret['opportunityType'] = OpportunityTypeSerializer(instance.opportunityType).data if instance.opportunityType else None
        ret['status_opportunity'] = StatusOpportunitySerializer(instance.status_opportunity).data if instance.status_opportunity else None
        ret['commercial_activity'] = CommercialActivitySerializer(instance.commercial_activity.all(), many=True).data
        ret['finance_opportunities'] = FinanceOpportunitySerializer(instance.financeopportunity_set.all(), many=True).data
        return ret
