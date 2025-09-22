import logging

from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.utils.functional import cached_property
from rest_framework import status
from rest_framework.response import Response

from catalog.viewsets.base import CachedViewSet
from core.di import injector
from opportunity.models import OpportunityDocument
from opportunity.serializers import (OpportunityDocumentSerializer
                                     )
from opportunity.services.opportunity_service import OpportunityService

logger = logging.getLogger(__name__)

class OpportunityDocumentViewSet(CachedViewSet):
    model = OpportunityDocument
    serializer_class = OpportunityDocumentSerializer

    # Configuración específica de Opportunity
    cache_prefix = "opportunity"  # Override del "catalog" por defecto

    # Configuración para invalidaciones automáticas
    write_serializer_class = OpportunityDocumentSerializer  # Para invalidaciones automáticas
    read_serializer_class = OpportunityDocumentSerializer  # Para respuestas optimizadas

    @cached_property
    def opportunity_service(self) -> OpportunityService:
        return injector.get(OpportunityService)


    def get_queryset(self):
        user = self.request.user
        return self.opportunity_service.get_filtered_documents_queryset(user)


    def get_serializer_class(self):
        return (
            OpportunityDocumentSerializer
            if self.action in ('list', 'retrieve')
            else OpportunityDocumentSerializer
        )

    def get_actives_queryset(self, request):
        user = request.user
        return self.opportunity_service.get_base_documents_queryset(user).distinct()
        
    def destroy(self, request, *args, **kwargs):
        """
        Eliminar un documento específico de una oportunidad.
        URL: DELETE /api/opportunities/documents/{document_id}/
        """
        try:
            doc = self.get_object()
            result = self.opportunity_service.delete_document(doc)
            return Response(result, status=status.HTTP_200_OK)
        except Http404:
            return Response(status=status.HTTP_204_NO_CONTENT)

        except ObjectDoesNotExist:
            return Response({"error": "Documento no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            print(f" Error al eliminar documento: {e}")
            return Response({"error": "Error interno del servidor"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
