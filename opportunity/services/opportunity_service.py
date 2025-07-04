import logging

from django.db import IntegrityError
from django.db import transaction
from django.utils import timezone
from injector import inject
from rest_framework.exceptions import ValidationError

from catalog.constants import StatusIDs, StatusPurchaseTypeIDs
from catalog.models import LostOpportunityType
from opportunity.models import Opportunity, OpportunityDocument
from opportunity.services.interfaces import AbstractFinanceOpportunityFactory, AbstractLostOpportunityFactory
from opportunity.tasks import upload_to_sharepoint, delete_file_from_sharepoint
from purchase.models import PurchaseStatus

logger = logging.getLogger(__name__)


class OpportunityService:
    @inject
    def __init__(self, finance_factory: AbstractFinanceOpportunityFactory,
                 lost_opportunity_factory: AbstractLostOpportunityFactory):
        self.finance_factory = finance_factory
        self.lost_opportunity_factory = lost_opportunity_factory

    def process_create(self, serializer, request, files=None) -> Opportunity:
        serializer.validated_data["date_status"] = timezone.now()
        try:
            opportunity = serializer.save(
                agent=request.user,
                date_status=timezone.now())

            PurchaseStatus.objects.create_or_update(
                opportunity=opportunity,
                purchase_status_type_id=StatusPurchaseTypeIDs.PENDING,
            )

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

            # --- Manejar eliminación de documentos ---
            deleted_ids = request_data.get('deleted_documents', [])
            if deleted_ids:
                self._delete_opportunity_documents(instance, deleted_ids)

            # Si es GANADA y hay datos financieros → crear/actualizar FinanceOpportunity
            if new_status and new_status.id == StatusIDs.WON and finance_data:
                self.finance_factory.create_or_update(
                    opportunity=instance,
                    cost_subtotal=finance_data.get("cost_subtotal", 0),
                    offer_subtotal=finance_data.get("offer_subtotal", 0),
                    earned_amount=finance_data.get("earned_amount", 0),
                    order_closing_date=finance_data.get("order_closing_date")
                )

            # Si es PERDIDA → guardar tipo de oportunidad perdida
            if new_status and new_status.id == StatusIDs.LOST:
                lost_type_id = request_data.get("lost_opportunity_type")
                try:
                    lost_type = LostOpportunityType.objects.get(id=lost_type_id)
                except LostOpportunityType.DoesNotExist:
                    logger.error(f"[LOST TYPE NOT FOUND] ID={lost_type_id}")
                    raise ValidationError({"lost_opportunity_type": "El tipo de oportunidad perdida no existe."})

                self.lost_opportunity_factory.create_or_update(
                    opportunity=instance,
                    lost_opportunity_type=lost_type
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
            return

        for file in files:
            self._validate_file(file)

            file_data = file.read()
            file_name = file.name

            udn_name = (
                    getattr(instance.project, "work_cell", None)
                    and getattr(instance.project.work_cell, "udn", None)
                    and getattr(instance.project.work_cell.udn, "name", None)
            )

            if udn_name:
                transaction.on_commit(
                    lambda f_data=file_data, f_name=file_name:
                    upload_to_sharepoint.delay(udn_name, instance.pk, f_data, f_name)
                )

    def _delete_opportunity_documents(self, instance: Opportunity, document_ids: list):
        documents = OpportunityDocument.objects.filter(opportunity=instance, id__in=document_ids)
        for doc in documents:
            try:
                delete_file_from_sharepoint.delay(doc.sharepoint_url, doc.id)
                logger.info(f"🗑️ Documento eliminado: {doc.file_name}")
            except Exception as e:
                logger.warning(f"⚠️ No se pudo eliminar el archivo {doc.file_name} de SharePoint: {e}")





