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
            'agent', 'client', 'lost_opportunity', 'date_limit_send',
            'number_items', 'order_closing_date'
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
            'lost_opportunity', 'date_limit_send', 'number_items',
            'order_closing_date'
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
        Validación cruzada robusta (soporta PATCH parciales como reactivar con solo is_removed).
        """
        errors = {}

        # ===== Utilidades =====
        def to_decimal(val):
            if val is None:
                return None
            try:
                return Decimal(str(val))
            except (InvalidOperation, TypeError, ValueError):
                return None

        def validate_datetime_field(field_value):
            if field_value is not None and not isinstance(field_value, datetime):
                return "La fecha debe ser un valor datetime válido."
            return None

        # ===== Fechas (tipos y lógica básica) =====
        date_reception = attrs.get("date_reception", getattr(self.instance, "date_reception", None))
        date_status = attrs.get("date_status", getattr(self.instance, "date_status", None))
        sent_date = attrs.get("sent_date", getattr(self.instance, "sent_date", None))

        field_type_checks = {
            'date_reception': validate_datetime_field(date_reception),
            'date_status': validate_datetime_field(date_status),
            'sent_date': validate_datetime_field(sent_date),
        }
        for k, maybe_err in field_type_checks.items():
            if maybe_err:
                errors[k] = maybe_err

        if sent_date and date_reception and sent_date < date_reception:
            errors['sent_date'] = "La fecha de envío no puede ser anterior a la de recepción."

        # ===== Estado de la oportunidad (desde request o instancia) =====
        status_obj = attrs.get("status_opportunity", getattr(self.instance, "status_opportunity", None))
        status_id = getattr(status_obj, "id", None)

        # ===== Amount y earned_amount =====
        # amount propuesto o actual
        amount_in_request = attrs.get('amount', getattr(self.instance, 'amount', None))
        amount_dec = to_decimal(amount_in_request)

        # Tomar finance_opportunity del request o el actual (para earned_amount y order_closing_date)
        finance_data_req = attrs.get('finance_opportunity')
        earned_dec = None
        order_closing_date = None

        if isinstance(finance_data_req, dict):
            earned_dec = to_decimal(finance_data_req.get('earned_amount'))
            order_closing_date = finance_data_req.get('order_closing_date')

        # Si no llegó info financiera en el request, intenta leer de la instancia
        if (earned_dec is None or order_closing_date is None) and self.instance is not None:
            # OJO: asegúrate de usar el nombre correcto del related: finance_data vs finance_opportunity
            # Ajusta una sola vez y úsalo siempre igual:
            finance_related_name = 'finance_data'  # o 'finance_opportunity' según tu modelo real
            existing_finance = getattr(self.instance, finance_related_name, None)
            if existing_finance:
                if earned_dec is None:
                    earned_dec = to_decimal(getattr(existing_finance, 'earned_amount', None))
                if order_closing_date is None:
                    order_closing_date = getattr(existing_finance, 'order_closing_date', None)

        # ===== Regla: amount >= earned_amount cuando está WON =====
        # Solo valida si se conoce el estado y hay ambos valores
        if status_id is not None and status_id == StatusIDs.WON:
            if amount_dec is not None and earned_dec is not None and amount_dec < earned_dec:
                errors['amount'] = (
                    f'El monto ({amount_dec}) no puede ser menor que el monto ganado ({earned_dec}) '
                    f'para oportunidades ganadas.'
                )

        # ===== Reglas por estado (solo si conocemos el estado) =====
        states_requiring_fields = [StatusIDs.SEND, StatusIDs.NEGOTIATING, StatusIDs.WON]

        currency = attrs.get("currency", getattr(self.instance, "currency", None))
        lost_opportunity = attrs.get("lost_opportunity", getattr(self.instance, "lost_opportunity", None))

        if status_id in states_requiring_fields:
            if not currency:
                errors[
                    'currency'] = 'La moneda es obligatoria para oportunidades en el estado de la oportunidad seleccionada.'

            if amount_dec is None or amount_dec <= 0:
                errors[
                    'amount'] = 'El monto debe ser mayor a 0 para oportunidades en el estado de la oportunidad seleccionada.'

            # earned_amount > 0 cuando se exige (por ejemplo, WON)
            if status_id == StatusIDs.WON:
                if earned_dec is None or earned_dec <= 0:
                    errors['earned_amount'] = 'El monto ganado debe ser mayor a 0 para oportunidades ganadas.'
                # order_closing_date requerido en WON
                if not order_closing_date:
                    errors['order_closing_date'] = 'La fecha de cierre es obligatoria para oportunidades ganadas.'

        # Perdidas
        if status_id == StatusIDs.LOST:
            if not lost_opportunity:
                errors['lost_opportunity'] = 'El tipo de pérdida es obligatorio para oportunidades perdidas.'
            if not currency:
                errors['currency'] = 'La moneda es obligatoria para oportunidades perdidas.'
            if amount_dec is None or amount_dec <= 0:
                errors['amount'] = 'El monto debe ser mayor a 0 para oportunidades perdidas.'

        # ===== Resultado =====
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


