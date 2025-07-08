from datetime import datetime

from django.db import transaction, IntegrityError
from django.db.models import Prefetch
from rest_framework import status
from rest_framework.exceptions import ValidationError, APIException
from rest_framework.response import Response
import logging
from rest_framework.decorators import action
from catalog.viewsets.base import CachedViewSet
from client.models import Client
from core.di import injector
from opportunity.services.opportunity_service import OpportunityService
from .models import Opportunity, CommercialActivity, OpportunityDocument
from .serializers import (
    OpportunitySerializer, OpportunityWriteSerializer,
    CommercialActivitySerializer
)
logger = logging.getLogger(__name__)

class OpportunityViewSet(CachedViewSet):
    model = Opportunity
    serializer_class = OpportunitySerializer

    def get_base_optimized_queryset(self):
        optimized_clients = Prefetch(
            'contact__clients',
            queryset=Client.objects.select_related('city', 'business_group')
        )

        optimized_finance = Prefetch(
            'finance_data',
            queryset=self.model._meta.get_field('finance_data').related_model.objects.all()
        )
        optimized_documents = Prefetch(
            'documents',
            queryset=OpportunityDocument.objects.only(
                'id', 'file_name', 'sharepoint_url', 'uploaded_at', 'opportunity'
            )
        )

        return (Opportunity.objects.select_related(
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
            'project__work_cell__udn'
        )
        .prefetch_related(
            optimized_finance,
            optimized_clients,
            optimized_documents
        ))


    def get_optimized_queryset(self):
        return self.get_base_optimized_queryset().filter(
            created__year=datetime.now().year
        ).distinct().order_by('-created')


    def get_queryset(self):
        return self.get_optimized_queryset()


    def get_serializer_class(self):
        return (
            OpportunitySerializer
            if self.action in ('list', 'retrieve')
            else OpportunityWriteSerializer
        )

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        print("🚀🚀🚀 METODO CREATE EJECUTANDOSE 🚀🚀🚀")  # ← AGREGA ESTA LÍNEA
        try:
            serializer = self.get_serializer(data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)

            # ✅ DEBUG: Capturar TODOS los archivos
            print(f"🔍 Todos los campos en request.FILES: {list(request.FILES.keys())}")
            print(f"🔍 request.FILES completo: {dict(request.FILES)}")
            
            files_documents = request.FILES.getlist('documents')
            files_files = request.FILES.getlist('files') 
            files_document = request.FILES.getlist('document')
            
            print(f"🔍 'documents': {len(files_documents)}")
            print(f"🔍 'files': {len(files_files)}")
            print(f"🔍 'document': {len(files_document)}")
            
            files = files_documents or files_files or files_document
            
            print(f"🔍 Archivos finales: {len(files)}")
            for i, file in enumerate(files):
                print(f"📁 Archivo {i+1}: {file.name}, tamaño: {file.size}")

            opportunity_service = injector.get(OpportunityService)
            opportunity = opportunity_service.process_create(serializer, request, files)

            opportunity = self.get_base_optimized_queryset().get(pk=opportunity.pk)

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

            opportunity = self.get_base_optimized_queryset().get(pk=opportunity.pk)

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
        print(f"🔍 DELETE recibido - User: {request.user}")
        print(f"🔍 Headers: {dict(request.headers)}")
        print(f"🔍 Auth: {request.auth}")       
        """
        Eliminar un documento específico de una oportunidad.
        
        URL: DELETE /api/opportunities/{opportunity_id}/documents/{document_id}/
        """
        try:
            opportunity = self.get_object()
            
            # Buscar el documento
            try:
                document = OpportunityDocument.objects.get(
                    id=document_id, 
                    opportunity=opportunity
                )
            except OpportunityDocument.DoesNotExist:
                return Response(
                    {"error": "Documento no encontrado"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            print(f"🗑️ Eliminando documento: {document.file_name}")
            
            # Eliminar de SharePoint de forma síncrona (para Windows)
            try:
                from opportunity.tasks import delete_file_from_sharepoint
                delete_file_from_sharepoint(document.sharepoint_url, document.id)
                print(f"✅ Documento eliminado de SharePoint: {document.file_name}")
            except Exception as e:
                print(f"⚠️ Error al eliminar de SharePoint: {e}")
                # Continuar eliminando de BD aunque falle SharePoint
            
            # Eliminar de base de datos
            document.delete()
            print(f"✅ Documento eliminado de BD: {document.file_name}")
            
            return Response(
                {"message": f"Documento '{document.file_name}' eliminado exitosamente"}, 
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            print(f"❌ Error al eliminar documento: {e}")
            return Response(
                {"error": "Error interno del servidor"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CommercialActivityViewSet(CachedViewSet):
    model = CommercialActivity
    serializer_class = CommercialActivitySerializer


