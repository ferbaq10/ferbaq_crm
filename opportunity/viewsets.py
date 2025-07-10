import logging

from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction, IntegrityError
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError, APIException
from rest_framework.response import Response

from catalog.viewsets.base import CachedViewSet
from core.di import injector
from opportunity.services.opportunity_service import OpportunityService
from .models import Opportunity, CommercialActivity
from .serializers import (
    OpportunitySerializer, OpportunityWriteSerializer,
    CommercialActivitySerializer
)

logger = logging.getLogger(__name__)

class OpportunityViewSet(CachedViewSet):
    model = Opportunity
    serializer_class = OpportunitySerializer


    def get_queryset(self):
        opportunity_service = injector.get(OpportunityService)
        return opportunity_service.get_filtered_queryset()


    def get_serializer_class(self):
        return (
            OpportunitySerializer
            if self.action in ('list', 'retrieve')
            else OpportunityWriteSerializer
        )

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)

            files_documents = request.FILES.getlist('documents')
            files_files = request.FILES.getlist('files') 
            files_document = request.FILES.getlist('document')
            
            files = files_documents or files_files or files_document

            opportunity_service = injector.get(OpportunityService)
            opportunity = opportunity_service.process_create(serializer, request, files)

            opportunity = opportunity_service.get_base_optimized_queryset().get(pk=opportunity.pk)

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
            instance = self.get_object()
            partial = kwargs.pop('partial', request.method == 'PATCH')
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)

            files = request.FILES.getlist('documents')

            opportunity_service = injector.get(OpportunityService)
            opportunity = opportunity_service.process_update(serializer, request.data, files)

            opportunity = opportunity_service.get_base_queryset().get(pk=opportunity.pk)

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
        
    @action(detail=True, methods=['delete'], url_path='documents/(?P<document_id>[^/.]+)')
    def delete_document(self, request, pk=None, document_id=None):
        """
        Eliminar un documento específico de una oportunidad.
        URL: DELETE /api/opportunities/{opportunity_id}/documents/{document_id}/
        """
        try:
            opportunity = self.get_object()
            opportunity_service = injector.get(OpportunityService)
            result = opportunity_service.delete_document(opportunity, document_id)
            return Response(result, status=status.HTTP_200_OK)

        except ObjectDoesNotExist:
            return Response({"error": "Documento no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            print(f" Error al eliminar documento: {e}")
            return Response({"error": "Error interno del servidor"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CommercialActivityViewSet(CachedViewSet):
    model = CommercialActivity
    serializer_class = CommercialActivitySerializer


