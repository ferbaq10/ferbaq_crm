from datetime import datetime

from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from catalog.constants import StatusIDs
from catalog.models import OpportunityType, StatusOpportunity, Currency, LostOpportunityType
from catalog.serializers import StatusOpportunitySerializer, CurrencySerializer, OpportunityTypeSerializer, \
    LostOpportunityTypeSerializer
from client.models import Client
from client.serializers import ClientSerializer
from contact.models import Contact
from contact.serializers import ContactSerializer
from project.models import Project
from project.serializers import ProjectSerializer
from users.serializers import UserSerializer
from .models import CommercialActivity, FinanceOpportunity, Opportunity, OpportunityDocument
from decimal import Decimal, InvalidOperation


User = get_user_model()

class OpportunityDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = OpportunityDocument
        fields = ['id', 'file_name', 'sharepoint_url', 'uploaded_at']

class FinanceOpportunitySerializer(serializers.ModelSerializer):
    class Meta:
        model = FinanceOpportunity
        fields = [
            'id',
            'is_removed',
            'earned_amount',
            'cost_subtotal',
            'order_closing_date',
            'oc_number'
        ]
        read_only_fields = ['created', 'modified']


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
        read_only_fields = ['created', 'modified']


# --- Opportunity SOLO LECTURA ---
class OpportunitySerializer(serializers.ModelSerializer):
    contact = ContactSerializer()
    agent = UserSerializer()
    project = ProjectSerializer()
    currency = CurrencySerializer()
    opportunityType = OpportunityTypeSerializer()
    status_opportunity = StatusOpportunitySerializer()
    client = ClientSerializer()

    lost_opportunity = LostOpportunityTypeSerializer()

    finance_opportunity = FinanceOpportunitySerializer(
        source='finance_data',
        read_only=True
    )
    documents = OpportunityDocumentSerializer(many=True, read_only=True)

    class Meta:
        model = Opportunity
        fields = [
            'id', 'name', 'description', 'amount', 'requisition_number',
            'date_reception', 'sent_date', 'date_status',
            'status_opportunity', 'contact', 'currency',
            'project', 'opportunityType', 'closing_percentage',
            'finance_opportunity', 'is_removed', 'documents',
            'agent', 'client', 'lost_opportunity'
        ]
        read_only_fields = ['created', 'modified']


# --- Opportunity CREACIÓN / ACTUALIZACIÓN ---
class OpportunityWriteSerializer(serializers.ModelSerializer):
    name = serializers.CharField(
        max_length=100,
        required=True,
        error_messages={
            'required': 'El nombre es obligatorio.',
            'min_length': 'El nombre debe tener un mínimo de 20 caracteres.',
            'max_length': 'El nombre no puede exceder los 100 caracteres.',
            'unique': 'Ya existe una oportunidad con este nombre.'
        }
    )
    project = serializers.PrimaryKeyRelatedField(queryset=Project.objects.all(), write_only=True)
    contact = serializers.PrimaryKeyRelatedField(queryset=Contact.objects.all(), write_only=True)
    client = serializers.PrimaryKeyRelatedField(queryset=Client.objects.all(), write_only=True)
    currency = serializers.PrimaryKeyRelatedField(
        queryset=Currency.objects.all(),
        write_only=True,
        required=False,
        allow_null=True
    )
    opportunityType = serializers.PrimaryKeyRelatedField(queryset=OpportunityType.objects.all(), write_only=True)
    status_opportunity = serializers.PrimaryKeyRelatedField(queryset=StatusOpportunity.objects.all(), write_only=True)

    finance_opportunity = FinanceOpportunitySerializer(write_only=True, required=False)
    lost_opportunity = serializers.PrimaryKeyRelatedField(
        queryset=LostOpportunityType.objects.all(),
        write_only=True,
        required=False,
        default=None
    )

    class Meta:
        model = Opportunity
        fields = [
            'id', 'name', 'description', 'amount', 'requisition_number',
            'date_reception', 'sent_date', 'date_status',
            'status_opportunity', 'contact', 'currency',
            'project', 'opportunityType', 'closing_percentage',
            'finance_opportunity', 'is_removed', 'client',
            'lost_opportunity'
        ]
        extra_kwargs = {
            'requisition_number': {
            'error_messages': {
                'max_length': 'El número de requisición no puede tener más de 100 caracteres.'},
                'max_length': 100},
            'status_opportunity': {'error_messages': {'required': 'El estado es obligatorio.'}},
            'amount': {
                    'error_messages': {
                        'min_value': 'El monto debe ser mayor o igual a cero.',
                        'invalid': 'Ingrese un monto válido.',
                    },
                    'min_value': 0  # Valor mínimo permitido
            },
            'contact': {'error_messages': {'required': 'El contacto es obligatorio.'}},
            'project': {'error_messages': {'required': 'El proyecto es obligatorio.'}},
            'client': {'error_messages': {'required': 'El cliente es obligatorio.'}},
            'opportunityType': {'error_messages': {'required': 'El tipo de oportunidad es obligatorio.'}},
        }
        read_only_fields = ['created']

    def validate_amount(self, value):
        if value < 0:
            raise serializers.ValidationError("El monto debe ser mayor o igual a cero.")
        return value

    def validate(self, attrs):
        """
        Validación cruzada de campos para oportunidades.
        """
        # Extraer datos una sola vez
        sent_date = attrs.get("sent_date")
        date_status = attrs.get("date_status")
        date_reception = attrs.get("date_reception")
        status_opportunity = attrs.get("status_opportunity")
        amount = attrs.get("amount")
        currency = attrs.get("currency")
        order_closing_date = attrs.get("order_closing_date")
        lost_opportunity_type = attrs.get("lost_opportunity_type")

        errors = {}

        # ===========================
        # VALIDACIONES DE FECHAS
        # ===========================
        def validate_datetime_field(field_name, field_value):
            """Valida que un campo sea datetime válido"""
            if field_value is not None and not isinstance(field_value, datetime):
                return f"La fecha debe ser un valor datetime válido."
            return None

        # Validar tipos de fechas
        datetime_fields = {
            'date_reception': ('date_reception', date_reception),
            'date_status': ('date_status', date_status),
            'sent_date': ('sent_date', sent_date)
        }

        for field_key, (field_name, field_value) in datetime_fields.items():
            error_msg = validate_datetime_field(field_name, field_value)
            if error_msg:
                errors[field_key] = error_msg

        # Validar lógica de fechas
        if sent_date and date_reception and sent_date < date_reception:
            errors['sent_date'] = "La fecha de envío no puede ser anterior a la de recepción."

        # ===========================
        # VALIDACIÓN AMOUNT VS EARNED_AMOUNT
        # ===========================
        def to_decimal(val):
            """Convierte valor a Decimal de forma segura"""
            if val is None:
                return None
            try:
                return Decimal(str(val))
            except (InvalidOperation, TypeError, ValueError):
                return None

        # Obtener amount propuesto o actual
        amount_in_request = attrs.get('amount', getattr(self.instance, 'amount', None))
        amount_dec = to_decimal(amount_in_request)

        # Obtener earned_amount de finance_opportunity
        earned_dec = None
        finance_data = attrs.get('finance_opportunity')

        if isinstance(finance_data, dict):
            earned_in_request = finance_data.get('earned_amount')
            earned_dec = to_decimal(earned_in_request)

        # Si no hay earned_amount en request, buscar en instancia existente
        if earned_dec is None and self.instance is not None:
            try:
                existing_finance = getattr(self.instance, 'finance_opportunity', None)
                if existing_finance is not None:
                    earned_dec = to_decimal(getattr(existing_finance, 'earned_amount', None))
            except (ObjectDoesNotExist, AttributeError):
                earned_dec = None

        # Validar relación amount >= earned_amount para oportunidades ganadas
        if (amount_dec is not None and
                earned_dec is not None and
                status_opportunity == StatusIDs.WON and
                amount_dec < earned_dec):
            errors['amount'] = (
                f'El monto ({amount_dec}) no puede ser menor que el monto ganado '
                f'({earned_dec}) para oportunidades ganadas.'
            )

        # ===========================
        # VALIDACIONES POR ESTADO
        # ===========================

        # Estados que requieren campos obligatorios
        states_requiring_fields = [StatusIDs.SEND, StatusIDs.NEGOTIATING, StatusIDs.WON]

        if status_opportunity.id in states_requiring_fields:
            if not currency:
                errors['currency'] = (
                    'La moneda es obligatoria para oportunidades en el estado de la oportunidad seleccionada.'
                )

            if not amount or amount <= 0:
                errors['amount'] = (
                    'El monto debe ser mayor a 0 para oportunidades en el estado de la oportunidad seleccionada.'
                )

            if not earned_dec or earned_dec <= 0:
                errors['earned_amount'] = (
                    'El monto ganado debe ser mayor a 0 para oportunidades en el estado de la oportunidad ganada.'
                )

            if not order_closing_date and status_opportunity.id is not StatusIDs.WON:
                errors['order_closing_date'] = (
                    'La fecha de cierre es obligatoria para oportunidades en el estado de la oportunidad seleccionada.'
                )
            if not finance_data.get('order_closing_date') and StatusIDs.WON:
                errors['order_closing_date'] = (
                    'La fecha de cierre es obligatoria para oportunidades en el estado de la oportunidad seleccionada.'
                )

        # Validación específica para oportunidades perdidas
        if status_opportunity.id == StatusIDs.LOST:
            if not lost_opportunity_type:
                errors['lost_opportunity_type'] = (
                    'El tipo de pérdida es obligatorio para oportunidades en el estado de la oportunidad perdida.'
                )
            if not currency:
                errors['currency'] = (
                    'La moneda es obligatoria para oportunidades en el estado de la oportunidad seleccionada'
                )

            if not amount or amount <= 0:
                errors['amount'] = (
                    'El monto debe ser mayor a 0 para oportunidades en el estado de la oportunidad seleccionada.'
                )

        # ===========================
        # LANZAR ERRORES SI EXISTEN
        # ===========================
        if errors:
            raise serializers.ValidationError(errors)

        return attrs

    # NUEVO: Método update personalizado
    def update(self, instance, validated_data):
        print(f" Actualizando oportunidad {instance.id}: {instance.name}")
        
        # Extraer finance_opportunity del validated_data
        finance_data = validated_data.pop('finance_opportunity', None)
        
        # Actualizar campos principales de la oportunidad
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Manejar finance_opportunity si viene en los datos
        if finance_data:
            print(f" Procesando finance_data: {finance_data}")
            try:
                # Intentar obtener FinanceOpportunity existente
                finance_obj = instance.finance_data
                print(f" FinanceOpportunity existente encontrado, actualizando...")
                
                # Actualizar campos
                for field, value in finance_data.items():
                    setattr(finance_obj, field, value)
                finance_obj.save()
                
            except FinanceOpportunity.DoesNotExist:
                print(f" No existe FinanceOpportunity, creando nuevo...")
                
                # Crear nuevo FinanceOpportunity
                finance_obj = FinanceOpportunity.objects.create(
                    opportunity=instance,
                    **finance_data
                )
                print(f" FinanceOpportunity creado: {finance_obj}")
                
        instance.refresh_from_db()
        return instance

    # ACTUALIZADO: Método create para manejar finance_opportunity
    def create(self, validated_data):
        # Extraer finance_opportunity del validated_data
        finance_data = validated_data.pop('finance_opportunity', None)
        
        # Establecer el usuario
        validated_data['agent'] = self.context['request'].user
        
        # Crear la oportunidad
        instance = super().create(validated_data)
        
        # Crear FinanceOpportunity si viene en los datos
        if finance_data:
            print(f"🔍 Creando FinanceOpportunity para nueva oportunidad: {finance_data}")
            FinanceOpportunity.objects.create(
                opportunity=instance,
                **finance_data
            )
            
        return instance


