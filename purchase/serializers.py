from rest_framework import serializers
from rest_framework.exceptions import MethodNotAllowed

from catalog.models import PurchaseStatusType
from catalog.serializers import PurchaseStatusTypeSerializer, StatusOpportunitySerializer, CurrencySerializer, \
    OpportunityTypeSerializer
from contact.serializers import ContactSerializer
from opportunity.models import Opportunity
from opportunity.serializers import FinanceOpportunitySerializer
from project.serializers import ProjectSerializer
from .models import PurchaseStatus


class PurchaseStatusSerializer(serializers.ModelSerializer):
    purchase_status_type = PurchaseStatusTypeSerializer(read_only=True)

    class Meta:
        model = PurchaseStatus
        fields = ['id', 'is_removed', 'purchase_status_type']
        read_only_fields = ['id', 'is_removed']



class PurchaseOpportunitySerializer(serializers.ModelSerializer):
    status_opportunity = StatusOpportunitySerializer(read_only=True)
    currency = CurrencySerializer(read_only=True)
    opportunityType = OpportunityTypeSerializer(read_only=True)
    contact = ContactSerializer(read_only=True)
    project = ProjectSerializer(read_only=True)

    finance_opportunity = FinanceOpportunitySerializer(
        source='finance_data',
        read_only=True
    )

    status_purchase = PurchaseStatusSerializer(
        source='purchase_data',
        read_only=True
    )

    class Meta:
        model = Opportunity
        fields = [
            'id', 'name', 'description', 'amount', 'number_fvt',
            'date_reception', 'sent_date', 'date_status',
            'status_opportunity', 'currency', 'opportunityType',
            'contact', 'project', 'finance_opportunity',
            'status_purchase', 'is_removed'
        ]
        read_only_fields = ['id', 'created', 'modified']



# --- Purchase CREACIÓN / ACTUALIZACIÓN ---
class PurchaseStatusWriteSerializer(serializers.ModelSerializer):
    purchase_status_type = serializers.PrimaryKeyRelatedField(
        queryset=PurchaseStatusType.objects.all(),
        required=True,
        error_messages={
            'required': 'El tipo de estatus de compra es obligatorio.',
            'does_not_exist': 'El tipo de estatus de compra seleccionado no existe.',
            'incorrect_type': 'El valor proporcionado no es un ID válido.'
        }
    )

    opportunity = serializers.PrimaryKeyRelatedField(
        queryset=Opportunity.objects.all(),
        required=True,
        error_messages={
            'required': 'La oportunidad es obligatoria.',
            'does_not_exist': 'La oportunidad seleccionada no existe.',
            'incorrect_type': 'El valor proporcionado no es un ID válido.'
        }
    )

    class Meta:
        model = PurchaseStatus
        fields = ['id', 'purchase_status_type', 'opportunity']

    def validate(self, data):
        # Validación adicional (opcional): evitar duplicados
        opportunity = data.get('opportunity')

        existing = PurchaseStatus.objects.filter(opportunity=opportunity)
        if self.instance:
            # Si estamos en update, excluirse a sí mismo
            existing = existing.exclude(pk=self.instance.pk)

        if existing.exists():
            raise serializers.ValidationError({
                'opportunity': 'Ya existe un estado de compra registrado para esta oportunidad.'
            })

        return data

    def create(self, request, *args, **kwargs):
        raise MethodNotAllowed("POST", detail="No está permitido crear oportunidades desde este endpoint.")