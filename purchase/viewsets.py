from datetime import datetime

from django.db import IntegrityError
from django.db.models import Prefetch
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.exceptions import ValidationError, APIException
from rest_framework.response import Response

from catalog.viewsets.base import CachedViewSet
from client.models import Client
from core.di import injector
from opportunity.models import Opportunity
from purchase.serializers import PurchaseOpportunitySerializer, PurchaseWriteSerializer
from purchase.services.purchase_service import PurchaseService


class PurchaseViewSet(CachedViewSet):
    model = Opportunity
    serializer_class = PurchaseOpportunitySerializer
    NEGOTIATING_STATUS_ID = 4  # Id del estado de la oportunidad 'Negociando'
    CLOSING_PERCENTAGE = 80
    AMOUNT_MXN = 250000
    AMOUNT_USD = 13000
    CURRENCY_MN = 1 # ID de la divisa para MN
    CURRENCY_USD = 2 # ID de la divisa para USD

    def get_queryset(self):
        return self.get_optimized_queryset()

    def get_serializer_class(self):
        return (
            PurchaseOpportunitySerializer
            if self.action in ('list', 'retrieve')
            else PurchaseWriteSerializer
        )

    def get_object(self):
        """
        En update, necesitamos evitar filtrar por año, monto, etc.
        """
        queryset = Opportunity.objects.select_related(
            'purchase_data',
            'purchase_data__purchase_status_type'
        )
        return get_object_or_404(queryset, pk=self.kwargs.get('pk'))


    def update(self, request, *args, **kwargs):
        try:
            opportunity = self.get_object()
            serializer = PurchaseWriteSerializer(opportunity, data=request.data, partial=True)

            serializer.is_valid(raise_exception=True)
            validated = serializer.validated_data

            purchase_service = injector.get(PurchaseService)
            opportunity = purchase_service.process_update(opportunity, validated, request.data)
            return Response(self.get_serializer(opportunity).data, status=status.HTTP_200_OK)

        except ValidationError as e:
            raise
        except IntegrityError:
            # Traducción la excepción de DB a un ValidationError de DRF
            raise ValidationError({
                'non_field_errors': ['Error de integridad en base de datos.']
            })
        except Exception as e:
            print(e)
            raise APIException('Error interno del servidor.')

    def get_optimized_queryset(self):
        # Optimizar consultas de oportunidad
        optimized_clients = Prefetch(
            'contact__clients',
            queryset=Client.objects.select_related('city', 'business_group')
        )

        # Optimizar datos financieros
        optimized_finance = Prefetch(
            'finance_data',
            queryset=self.model._meta.get_field('finance_data').related_model.objects.all()
        )

        current_year = datetime.now().year

        return Opportunity.objects.select_related(
            # Status y tipos básicos
            'status_opportunity',
            'currency',
            'opportunityType',

            # Contacto y sus relaciones
            'contact',
            'contact__job',
            'contact__city',

            # Proyecto y todas sus relaciones
            'project',
            'project__client',
            'project__client__city',
            'project__client__business_group',
            'project__specialty',
            'project__subdivision',
            'project__subdivision__division',
            'project__project_status',
            'project__work_cell',
            'project__work_cell__udn',

            # PurchaseStatus y su tipo
            'purchase_data',
            'purchase_data__purchase_status_type'  # <-- ¡esta línea es clave!
        ).prefetch_related(
            optimized_finance,
            optimized_clients
        ).filter(
            created__year=current_year,
            closing_percentage__gte=self.CLOSING_PERCENTAGE,
            status_opportunity_id=self.NEGOTIATING_STATUS_ID
        ).filter(
            Q(currency_id=self.CURRENCY_MN, amount__gte=self.AMOUNT_MXN) |
            Q(currency_id=self.CURRENCY_USD, amount__gte=self.AMOUNT_USD)
        ).distinct().order_by('-created')
