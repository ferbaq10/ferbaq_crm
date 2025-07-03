from datetime import datetime

from django.db import IntegrityError
from django.db.models import Prefetch
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.exceptions import ValidationError, APIException
from rest_framework.response import Response

from catalog.constants import CurrencyIDs, StatusIDs, OpportunityFilters
from catalog.viewsets.base import CachedViewSet
from client.models import Client
from core.di import injector
from opportunity.models import Opportunity
from purchase.serializers import PurchaseOpportunitySerializer, PurchaseWriteSerializer, PurchaseStatusSerializer
from purchase.services.purchase_service import PurchaseService


class PurchaseViewSet(CachedViewSet):
    model = Opportunity
    serializer_class = PurchaseOpportunitySerializer

    def _get_base_optimized_queryset(self):
        optimized_clients = Prefetch(
            'contact__clients',
            queryset=Client.objects.select_related('city', 'business_group')
        )

        optimized_finance = Prefetch(
            'finance_data',
            queryset=self.model._meta.get_field('finance_data').related_model.objects.all()
        )

        return Opportunity.objects.select_related(
            'status_opportunity',
            'currency',
            'opportunityType',
            'contact',
            'contact__job',
            'contact__city',
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
            'purchase_data',
            'purchase_data__purchase_status_type'
        ).prefetch_related(
            optimized_clients,
            optimized_finance
        )

    def get_queryset(self):
        current_year = datetime.now().year
        return self._get_base_optimized_queryset().filter(
            created__year=current_year,
            closing_percentage__gte=OpportunityFilters.CLOSING_PERCENTAGE,
        ).filter(
            Q(currency_id=CurrencyIDs.MN, amount__gte=OpportunityFilters.AMOUNT_MN) |
            Q(currency_id=CurrencyIDs.USD, amount__gte=OpportunityFilters.AMOUNT_USD)
        ).filter(
            Q(status_opportunity_id=StatusIDs.NEGOTIATING) |
            Q(status_opportunity_id=StatusIDs.WON)
        ).distinct().order_by('-created')

    def get_serializer_class(self):
        return (
            PurchaseOpportunitySerializer
            if self.action in ('list', 'retrieve')
            else PurchaseWriteSerializer
        )

    def get_object(self):
        opportunity_id = self.kwargs.get("pk")
        queryset = self._get_base_optimized_queryset()
        return get_object_or_404(queryset, pk=opportunity_id)


    def update(self, request, *args, **kwargs):
        try:
            opportunity = self.get_object()
            serializer = PurchaseWriteSerializer(opportunity, data=request.data, partial=True)

            serializer.is_valid(raise_exception=True)
            validated = serializer.validated_data

            purchase_service = injector.get(PurchaseService)
            opportunity = purchase_service.process_update(opportunity, validated, request.data)
            response_serializer = PurchaseOpportunitySerializer(opportunity)
            return Response(response_serializer.data, status=status.HTTP_200_OK)

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
