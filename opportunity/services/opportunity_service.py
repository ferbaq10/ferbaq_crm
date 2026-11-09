import logging
from datetime import datetime
from typing import TypeVar

from django.db import IntegrityError, transaction
from django.db.models import Prefetch, QuerySet
from django.utils import timezone
from injector import inject
from rest_framework.exceptions import ValidationError

import django_rq

from catalog.constants import StatusIDs, StatusPurchaseTypeIDs
from catalog.models import WorkCell
from opportunity.models import Opportunity, FinanceOpportunity, OpportunityDocument
from opportunity.services.base import BaseService
from opportunity.services.interfaces import AbstractFinanceOpportunityFactory
from opportunity.tasks import upload_to_sharepoint_db, delete_file_from_sharepoint_db
from purchase.models import PurchaseStatus

T = TypeVar('T')
logger = logging.getLogger(__name__)


class OpportunityService(BaseService):

    @inject
    def __init__(self, finance_factory: AbstractFinanceOpportunityFactory):
        self.finance_factory = finance_factory

    # =========================================================
    # QUERYSETS
    # =========================================================

    def get_prefetched_queryset(self):
        return (
            Opportunity.objects
            .select_related(
                'status_opportunity',
                'contact__job',
                'currency',
                'agent', 'agent__profile',
                'project__project_status',
                'project__specialty',
                'project__subdivision__division',
                'project__work_cell__udn',
                'opportunityType',
                'client__city',
                'client__business_group',
                'lost_opportunity',
            )
            .prefetch_related(
                Prefetch(
                    'documents',
                    queryset=OpportunityDocument.objects.only(
                        'id', 'file_name', 'sharepoint_url',
                        'uploaded_at', 'opportunity_id'
                    ),
                ),
                Prefetch(
                    'finance_data',
                    queryset=FinanceOpportunity.objects.only(
                        'id', 'earned_amount', 'cost_subtotal',
                        'order_closing_date', 'oc_number',
                        'cash_percentage', 'credit_percentage',
                        'opportunity_id', 'is_removed'
                    ),
                ),
                Prefetch(
                    'agent__workcell',
                    queryset=WorkCell.objects
                        .select_related('udn')
                        .only('id', 'name', 'udn_id'),
                ),
            )
        )

    def get_base_queryset(self, user):
        return self.add_filter_by_rol(
            user,
            self.get_prefetched_queryset(),
            owner_field='agent'
        )

    def get_filtered_queryset(self, user):
        return self.get_base_queryset(user).order_by('-created')

    # =========================================================
    # CREATE
    # =========================================================

    def process_create(self, serializer, request, files=None) -> Opportunity:
        serializer.validated_data["date_status"] = timezone.now()

        opportunity = serializer.save(
            agent=request.user,
            date_status=timezone.now()
        )

        PurchaseStatus.objects.update_or_create(
            opportunity=opportunity,
            defaults={
                'purchase_status_type_id': StatusPurchaseTypeIDs.PENDING,
            }
        )

        opportunity.refresh_from_db()

        self.upload_files_related(files, opportunity)

        return opportunity

    # =========================================================
    # UPDATE
    # =========================================================

    def process_update(self, serializer, request_data: dict, files=None) -> Opportunity:
        instance: Opportunity = serializer.instance
        validated_data = serializer.validated_data

        new_status = validated_data.get("status_opportunity")

        if new_status and new_status.id != instance.status_opportunity_id:
            validated_data["date_status"] = timezone.now()

        finance_data = validated_data.pop("finance_opportunity", {})

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        if new_status and new_status.id == StatusIDs.WON and finance_data:
            self.finance_factory.create_or_update(
                opportunity=instance,
                cost_subtotal=finance_data.get("cost_subtotal", 0),
                earned_amount=finance_data.get("earned_amount", 0),
                order_closing_date=finance_data.get("order_closing_date"),
                oc_number=finance_data.get("oc_number"),
                cash_percentage=finance_data.get("cash_percentage"),
                credit_percentage=finance_data.get("credit_percentage"),
            )

        instance.refresh_from_db()

        self.upload_files_related(files, instance)

        return instance

    # =========================================================
    # FILE VALIDATION
    # =========================================================

    def _validate_file(self, file):
        max_size = 4 * 1024 * 1024
        allowed_extensions = ('.pdf', '.docx', '.xlsx')

        if file.size > max_size:
            raise ValidationError({'documento': 'El archivo excede el tamaño permitido (4 MB).'})

        if not file.name.lower().endswith(allowed_extensions):
            raise ValidationError({'documento': 'Formato de archivo no permitido.'})

    # =========================================================
    # FILE UPLOAD (SEGURO)
    # =========================================================

    def upload_files_related(self, files, instance: Opportunity):
        if not files:
            logger.info("No hay archivos para subir")
            return

        for file in files:
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

            if not udn_name:
                logger.error(f"No se pudo obtener UDN para {file_name}")
                continue

            logger.info(f"🔥 Preparando upload async para {file_name} en UDN {udn_name}")

            transaction.on_commit(
                lambda udn=udn_name,
                       opp_id=instance.id,
                       f_data=file_data,
                       f_name=file_name:
                django_rq.enqueue(upload_to_sharepoint_db, udn, opp_id, f_data, f_name)
            )

    # =========================================================
    # DELETE
    # =========================================================

    def delete_document(self, document: OpportunityDocument) -> dict:
        try:
            django_rq.enqueue(delete_file_from_sharepoint_db, document.sharepoint_url, document.id)
        except Exception as e:
            logger.error(f"Error al eliminar documento: {e}")

        return {
            "message": f"Documento '{document.file_name}' eliminado exitosamente"
        }
