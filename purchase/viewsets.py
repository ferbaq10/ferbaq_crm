from django.db import IntegrityError
from django.shortcuts import get_object_or_404
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

    def get_queryset(self):
        purchase_service = injector.get(PurchaseService)
        return purchase_service.get_filtered_queryset()

    def get_serializer_class(self):
        return (
            PurchaseOpportunitySerializer
            if self.action in ('list', 'retrieve')
            else PurchaseWriteSerializer
        )

    def get_object(self):
        opportunity_id = self.kwargs.get("pk")
        purchase_service = injector.get(PurchaseService)
        queryset = purchase_service.get_base_optimized_queryset()
        return get_object_or_404(queryset, pk=opportunity_id)


    def update(self, request, *args, **kwargs):
        try:
            opportunity = self.get_object()
            serializer = PurchaseWriteSerializer(opportunity, data=request.data, partial=True)

            serializer.is_valid(raise_exception=True)

            purchase_service = injector.get(PurchaseService)
            opportunity = purchase_service.process_update(opportunity, request.data)
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
