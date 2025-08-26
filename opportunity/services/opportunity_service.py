import logging
from datetime import datetime
from typing import TypeVar

from django.db import IntegrityError
from django.db import transaction
from django.db.models import Prefetch
from django.utils import timezone
from django_rq import enqueue
from injector import inject
from rest_framework.exceptions import ValidationError

from catalog.constants import StatusIDs, StatusPurchaseTypeIDs
from client.models import Client
from opportunity.models import Opportunity
from opportunity.models import OpportunityDocument
from opportunity.services.base import BaseService
from opportunity.services.interfaces import AbstractFinanceOpportunityFactory
from opportunity.tasks import upload_to_sharepoint_db, delete_file_from_sharepoint_db
from project.models import Project
from purchase.models import PurchaseStatus
from django.db.models import QuerySet
from typing import TypeVar

# Si usas un modelo genérico para el queryset
T = TypeVar('T')
logger = logging.getLogger(__name__)

class OpportunityService(BaseService):
    @inject
    def __init__(self, finance_factory: AbstractFinanceOpportunityFactory):
        self.finance_factory = finance_factory

    def get_prefetched_queryset(self):
        # Optimizar proyectos con todas sus relaciones
        optimized_projects = Prefetch(
            'contact__clients__projects',
            queryset=Project.objects.select_related(
                'work_cell__udn',
                'specialty',
                'subdivision__division',
                'project_status'
            ).order_by('id')
        )

        # Optimizar clientes con city y business_group
        optimized_clients = Prefetch(
            'contact__clients',
            queryset=Client.objects.select_related(
                'city',
                'business_group'
            ).order_by('id')
        )

        return (
            Opportunity.objects
            .select_related(
                'status_opportunity',
                'currency',
                'opportunityType',
                'contact__job',
                'project__specialty',
                'project__subdivision__division',
                'project__project_status',
                'project__work_cell__udn',
                'client__city',
                'client__business_group',
                'agent__profile',
                'lost_opportunity',
            )
            .prefetch_related(
                optimized_clients,
                optimized_projects,
                'finance_data',
                'documents'
            )
            .order_by('created')
        )


    def get_base_queryset(self, user):
        return self.add_filter_by_rol(user, self.get_prefetched_queryset(), owner_field='agent')

    def get_filtered_queryset(self, user):
        return (self.add_filter_by_rol(user, self.get_prefetched_queryset())
                    .filter(is_removed=False).distinct())


    def get_base_documents_queryset(self, user) -> QuerySet[OpportunityDocument]:

        queryset = OpportunityDocument.objects.only('id', 'sharepoint_url')

        return self.add_filter_by_rol(user, queryset,
                                      workcell_filter_field="opportunity__project__work_cell__users",
                                      owner_field="opportunity__agent"
                                      )


    def get_filtered_queryset(self, user):
        return self.get_base_queryset(user).filter(
            created__year=datetime.now().year
        ).distinct().order_by('-created')

    def get_filtered_documents_queryset(self, user):
        return self.get_base_documents_queryset(user).filter(
            uploaded_at__year=datetime.now().year
        ).distinct().order_by('-uploaded_at')

    def process_create(self, serializer, request, files=None) -> Opportunity:
        serializer.validated_data["date_status"] = timezone.now()
        try:
            opportunity = serializer.save(
                agent=request.user,
                date_status=timezone.now())

            PurchaseStatus.objects.update_or_create(
                opportunity=opportunity,
                defaults={
                    'purchase_status_type_id': StatusPurchaseTypeIDs.PENDING,
                }
            )

            opportunity = Opportunity.objects.select_related(
                'project__work_cell__udn'
            ).get(pk=opportunity.pk)

            self.upload_files_related(files, opportunity)

            return opportunity
        except AttributeError as e:
            message = f"UDN no disponible para la oportunidad, no se subió archivo."
            logger.warning(f"{message} + {e}" )
            raise ValidationError({"non_field_errors": [message]})
        except IntegrityError as e:
            message = f"Error de integridad. {e}"
            logger.warning(message)
            raise

        except Exception as e:
            message = f"ERROR - en la creación de la oportunidad "
            logger.error(F"{message} {e}")
            raise ValidationError({"non_field_errors": [message]})

    def process_update(self, serializer, request_data: dict, files=None) -> Opportunity:
        instance: Opportunity = serializer.instance
        validated_data = serializer.validated_data
        try:
            # Actualizar fecha si cambia el estado
            new_status = validated_data.get("status_opportunity")
            if new_status and new_status.id != instance.status_opportunity_id:
                validated_data["date_status"] = timezone.now()

            # Extraer datos financieros si vienen
            finance_data = validated_data.pop("finance_opportunity", {})

            # Aplicar todos los campos actualizados
            for attr, value in validated_data.items():
                setattr(instance, attr, value)

            instance.save()

            # Si es GANADA y hay datos financieros → crear/actualizar FinanceOpportunity
            if new_status and (new_status.id == StatusIDs.WON) and finance_data:
                self.finance_factory.create_or_update(
                    opportunity=instance,
                    cost_subtotal=finance_data.get("cost_subtotal", 0),
                    earned_amount=finance_data.get("earned_amount", 0),
                    order_closing_date=finance_data.get("order_closing_date"),
                    oc_number=finance_data.get("oc_number"),
                    cash_percentage=finance_data.get("cash_percentage"),
                    credit_percentage = finance_data.get("credit_percentage")
                )

            # Subida de archivo si aplica
            self.upload_files_related(files, instance)

            # Refrescar relaciones por si se usan al serializar
            instance.refresh_from_db()

            return instance

        except ValidationError:
            raise
        except Exception as e:
            logger.error(f"[ERROR - process_update] {e}")
            raise ValidationError({"non_field_errors": ["Error al actualizar la oportunidad."]})

    def _validate_file(self, file):
        # 4 MB  TIENE UQE SER HASTA 4 MB PARA ELE ENVÍO A SHAREPOINT, SINO HAY QUE HACER OTRA SOLUCION
        max_size = 4 * 1024 * 1024
        allowed_extensions = ('.pdf', '.docx', '.xlsx')

        if file.size > max_size:
            raise ValidationError({'documento': 'El archivo excede el tamaño permitido (5 MB).'})

        if not file.name.lower().endswith(allowed_extensions):
            raise ValidationError({'documento': 'Formato de archivo no permitido.'})

    def upload_files_related(self, files, instance: Opportunity):
        if not files:
            print(" No hay archivos para subir")
            return

        for i, file in enumerate(files):
            try:
                self._validate_file(file)
            except ValidationError as e:
                logger.error(f"Archivo {file.name} falló validación: {e}")
                continue

            file_data = file.read()
            file_name = file.name
            udn_name = (
                    getattr(instance.project, "work_cell", None)
                    and getattr(instance.project.work_cell, "udn", None)
                    and getattr(instance.project.work_cell.udn, "name", None)
            )

            if udn_name:
                try:
                    transaction.on_commit(
                        lambda udn=udn_name,
                               id=instance.id,
                               f_data=file_data,
                               f_name=file_name:
                        enqueue(upload_to_sharepoint_db, udn, id, f_data, f_name)
                    )
                    # upload_to_sharepoint_db(udn_name, instance.id, file_data, file_name)
                    logger.info(f"Subido archivo {file_name}")
                    
                except Exception as e:
                    import traceback
                    traceback.print_exc()
                    logger.error(f" Error al subir {file_name}: {e}")
            else:
                logger.error(f"No se pudo obtener UDN para {file_name}")

    def delete_document(self, document: OpportunityDocument) -> dict:
        try:
            # Eliminar en SharePoint y BD
            delete_file_from_sharepoint_db(document.sharepoint_url, document.id)
        except Exception as e:
            logger.error(f" Error al eliminar en SharePoint o en base de datos: {e}")

        file_name = document.file_name
        return {"message": f"Documento '{file_name}' eliminado exitosamente"}