from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from django.utils.functional import cached_property
from rest_framework import status
from rest_framework.exceptions import ValidationError, APIException
from rest_framework.response import Response

from catalog.viewsets.base import CachedViewSet
from core.di import injector
from opportunity.models import Opportunity
from purchase.serializers import PurchaseOpportunitySerializer, PurchaseWriteSerializer, PurchaseStatusSerializer
from purchase.services.purchase_service import PurchaseService


class PurchaseViewSet(CachedViewSet):
    model = Opportunity
    serializer_class = PurchaseOpportunitySerializer

    # Configuración específica de Purchase
    cache_prefix = "purchase"  # Override del "catalog" por defecto

    # Configuración para invalidaciones automáticas
    write_serializer_class = PurchaseWriteSerializer  # Para invalidaciones automáticas
    read_serializer_class = PurchaseOpportunitySerializer  # Para respuestas optimizadas


    @cached_property
    def purchase_service(self) -> PurchaseService:
        return injector.get(PurchaseService)

    def get_queryset(self):
        user = self.request.user
        return self.purchase_service.get_filtered_queryset(user)

    def get_serializer_class(self):
        return (
            PurchaseOpportunitySerializer
            if self.action in ('list', 'retrieve')
            else PurchaseWriteSerializer
        )

    def get_object(self):
        user = self.request.user
        opportunity_id = self.kwargs.get("pk")
        queryset = self.purchase_service.get_base_optimized_queryset(user)
        return get_object_or_404(queryset, pk=opportunity_id)


    def update(self, request, *args, **kwargs):
        try:
            opportunity = self.get_object()
            serializer = PurchaseWriteSerializer(opportunity, data=request.data, partial=True)

            serializer.is_valid(raise_exception=True)

            opportunity = self.purchase_service.process_update(opportunity, request.data)
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
