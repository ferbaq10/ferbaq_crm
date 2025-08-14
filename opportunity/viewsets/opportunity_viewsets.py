import logging

from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction, IntegrityError
from django.utils.functional import cached_property
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError, APIException
from rest_framework.response import Response

from catalog.viewsets.base import CachedViewSet
from core.di import injector
from opportunity.models import Opportunity, CommercialActivity
from opportunity.serializers import (
    OpportunitySerializer, OpportunityWriteSerializer,
    CommercialActivitySerializer
)
from opportunity.services.opportunity_service import OpportunityService

logger = logging.getLogger(__name__)

class OpportunityViewSet(CachedViewSet):
    model = Opportunity
    serializer_class = OpportunitySerializer

    # Configuración específica de Opportunity
    cache_prefix = "opportunity"  # Override del "catalog" por defecto

    # Configuración para invalidaciones automáticas
    write_serializer_class = OpportunityWriteSerializer  # Para invalidaciones automáticas
    read_serializer_class = OpportunitySerializer  # Para respuestas optimizadas

    @cached_property
    def opportunity_service(self) -> OpportunityService:
        return injector.get(OpportunityService)


    def get_queryset(self):
        user = self.request.user
        return self.opportunity_service.get_filtered_queryset(user)


    def get_serializer_class(self):
        return (
            OpportunitySerializer
            if self.action in ('list', 'retrieve')
            else OpportunityWriteSerializer
        )

    def get_actives_queryset(self, request):
        user = request.user
        return self.opportunity_service.get_base_queryset(user).filter(is_removed=False).distinct()

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        try:
            user = request.user
            serializer = self.get_serializer(data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)

            files_documents = request.FILES.getlist('documents')

            opportunity = self.opportunity_service.process_create(serializer, request, files_documents)

            opportunity = self.opportunity_service.get_base_queryset(user).get(pk=opportunity.pk)

            return Response(OpportunitySerializer(opportunity).data, status=status.HTTP_200_OK)

        except ValidationError as e:
            raise
        except IntegrityError:
            raise ValidationError({
                'non_field_errors': ['Error de integridad en base de datos.']
            })
        except Exception as e:
            print(f"[ERROR - create()]: {e}")
            raise APIException('Error interno del servidor.')


    @transaction.atomic
    def update(self, request, *args, **kwargs):
        try:
            user = self.request.user
            instance = self.get_object()
            partial = kwargs.pop('partial', request.method == 'PATCH')
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)

            files = request.FILES.getlist('documents')

            opportunity = self.opportunity_service.process_update(serializer, request.data, files)

            opportunity = self.opportunity_service.get_base_queryset(user).get(pk=opportunity.pk)

            return Response(OpportunitySerializer(opportunity).data, status=status.HTTP_200_OK)

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

class CommercialActivityViewSet(CachedViewSet):
    model = CommercialActivity
    serializer_class = CommercialActivitySerializer


