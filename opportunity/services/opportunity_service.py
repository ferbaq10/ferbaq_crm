import logging
from django.db import transaction
from django.utils import timezone
from injector import inject
from rest_framework.exceptions import ValidationError

from catalog.constants import StatusIDs, StatusPurchaseTypeIDs
from catalog.models import LostOpportunityType
from opportunity.models import Opportunity
from opportunity.services.interfaces import AbstractFinanceOpportunityFactory, AbstractLostOpportunityFactory
from opportunity.tasks import upload_to_sharepoint
from purchase.models import PurchaseStatus

logger = logging.getLogger(__name__)


class OpportunityService:
    @inject
    def __init__(self, finance_factory: AbstractFinanceOpportunityFactory,
                 lost_opportunity_factory: AbstractLostOpportunityFactory):
        self.finance_factory = finance_factory
        self.lost_opportunity_factory = lost_opportunity_factory

    def process_create(self, validated_data: dict, request_data: dict, file=None) -> Opportunity:
        validated_data["date_status"] = timezone.now()

        try:
            opportunity = Opportunity.objects.create(**validated_data)

            PurchaseStatus.objects.create(
                opportunity=opportunity,
                purchase_status_type_id=StatusPurchaseTypeIDs.PENDING,
            )

            self.upload_file_related(file, opportunity)
            return opportunity
        except AttributeError:
            message = f"UDN no disponible para la oportunidad, no se subió archivo."
            logger.warning(message)
            raise ValidationError({"non_field_errors": [message]})

        except Exception as e:
            print(f"[ERROR - process_create]: {e}")
            raise ValidationError({"non_field_errors": ["Error al crear la oportunidad."]})


    def process_update(self, instance: Opportunity, validated_data: dict, request_data: dict, file=None) -> Opportunity:
        new_status = validated_data.get("status_opportunity")

        if new_status and new_status.id != instance.status_opportunity_id:
            validated_data["date_status"] = timezone.now()

        # Extraer objeto anidado de datos financieros (si se incluye)
        finance_data = validated_data.pop("finance_opportunity", {})

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()


        if new_status and new_status.id == StatusIDs.WON and finance_data:
            self.finance_factory.create_or_update(
                opportunity=instance,
                cost_subtotal=finance_data.get("cost_subtotal", 0),
                offer_subtotal=finance_data.get("offer_subtotal", 0),
                earned_amount=finance_data.get("earned_amount", 0),
                order_closing_date=finance_data.get("order_closing_date")
            )

        if new_status and new_status.id == StatusIDs.LOST:
            try:
                lost_opportunity_type = LostOpportunityType.objects.get(id=request_data.get("lost_opportunity_type"))

                self.lost_opportunity_factory.create_or_update(
                    opportunity=instance,
                    lost_opportunity_type=lost_opportunity_type
                )

            except LostOpportunityType.DoesNotExist:
                logger.error(f"El tipo de oportunidad perdida no existe.{request_data.get("lost_opportunity_type")}")
                raise ValidationError({"lost_opportunity_type": "El tipo de oportunidad perdida no existe."})

            except Exception as e:
                logger.error(f"Error al actualizar la oportunidad{e}")
                raise
        return instance

    def _validate_file(self, file):
        max_size = 5 * 1024 * 1024  # 5 MB
        allowed_extensions = ('.pdf', '.docx', '.xlsx')

        if file.size > max_size:
            raise ValidationError({'documento': 'El archivo excede el tamaño permitido (5 MB).'})

        if not file.name.lower().endswith(allowed_extensions):
            raise ValidationError({'documento': 'Formato de archivo no permitido.'})


    def upload_file_related(self, file, instance: Opportunity):
        if file:
            self._validate_file(file)

            # Leer binario antes de que se cierre la request
            file_data = file.read()
            file_name = file.name

            # Ejecutar tarea tras commit
            udn_name = (
                    getattr(instance.project, "work_cell", None)
                    and getattr(instance.project.work_cell, "udn", None)
                    and getattr(instance.project.work_cell.udn, "name", None)
            )

            udn_name = instance.project.work_cell.udn.name
            if udn_name:
                transaction.on_commit(
                    lambda: upload_to_sharepoint.delay(udn_name, instance.id, file_data, file_name)
                )