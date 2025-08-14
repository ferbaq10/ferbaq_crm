from datetime import datetime

from django.contrib.auth import get_user_model
from rest_framework import serializers

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
            'max_length': 'El nombre no puede exceder los 100 caracteres.',
            'unique': 'Ya existe una oportunidad con este nombre.'
        }
    )
    project = serializers.PrimaryKeyRelatedField(queryset=Project.objects.all(), write_only=True)
    contact = serializers.PrimaryKeyRelatedField(queryset=Contact.objects.all(), write_only=True)
    currency = serializers.PrimaryKeyRelatedField(queryset=Currency.objects.all(), write_only=True)
    client = serializers.PrimaryKeyRelatedField(queryset=Client.objects.all(), write_only=True)
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

    def validate(self, data):
        sent_date = data.get("sent_date")
        date_status = data.get("date_status")
        date_reception = data.get("date_reception")

        # Validar tipos datetime solo si los campos están presentes
        if date_reception is not None and not isinstance(date_reception, datetime):
            raise serializers.ValidationError({
                "date_reception": "La fecha de recepción debe ser un valor datetime válido."
            })

        if date_status is not None and not isinstance(date_status, datetime):
            raise serializers.ValidationError({
                "date_status": "La fecha del estado debe ser un valor datetime válido."
            })

        if sent_date is not None and not isinstance(sent_date, datetime):
            raise serializers.ValidationError({
                "sent_date": "La fecha de envío debe ser un valor datetime válido."
            })

        # Validar que sent_date no sea anterior a date_reception solo si ambos existen
        if sent_date and date_reception and sent_date < date_reception:
            raise serializers.ValidationError(
                "La fecha de envío no puede ser anterior a la de recepción."
            )

        return data

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


