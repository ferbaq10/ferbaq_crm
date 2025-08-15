import logging
from datetime import datetime
from typing import TypeVar

from django.contrib.auth.models import User
from django.db import IntegrityError
from django.db import transaction
from django.db.models import Prefetch
from django.db.models import QuerySet
from django.utils import timezone
from django_rq import enqueue
from injector import inject
from rest_framework.exceptions import ValidationError

from catalog.constants import StatusIDs, StatusPurchaseTypeIDs
from client.models import Client
from opportunity.models import Opportunity
from opportunity.models import OpportunityDocument
from opportunity.services.interfaces import AbstractFinanceOpportunityFactory
from opportunity.tasks import upload_to_sharepoint_db, delete_file_from_sharepoint_db
from purchase.models import PurchaseStatus
from users.models import RoleScope
from users.services.access import resolve_scope

# Si usas un modelo genérico para el queryset
T = TypeVar('T')
logger = logging.getLogger(__name__)

class OpportunityService:
    @inject
    def __init__(self, finance_factory: AbstractFinanceOpportunityFactory):
        self.finance_factory = finance_factory

    def add_filter_by_rol(self, user: User, queryset: QuerySet[T])-> QuerySet[T]:
        """
            Aplica un filtro al queryset de acuerdo con el alcance (scope) definido en las políticas de rol (RolePolicy) para el usuario.

            Modo de funcionamiento:
            1. Se obtiene el "scope" del usuario mediante la función resolve_scope(user), la cual determina el nivel de acceso
               revisando sus grupos y las políticas de rol configuradas en la base de datos.
               - RoleScope.ALL     → Acceso total a todos los registros.
               - RoleScope.WORKCELL → Acceso únicamente a registros ligados a la(s) célula(s) de trabajo (work_cell) en la(s) que participa el usuario.
               - RoleScope.OWNED   → Acceso únicamente a registros donde el usuario es el agente responsable.
               - RoleScope.NONE    → Sin acceso a registros.

            2. Según el scope obtenido:
               - Si es ALL: devuelve el queryset completo sin filtrar.
               - Si es WORKCELL: filtra por la relación project__work_cell__users para incluir solo los registros asociados a la(s) célula(s) del usuario.
               - Si es OWNED: filtra por el campo "agent" para incluir solo registros del propio usuario.
               - En cualquier otro caso (NONE): devuelve queryset vacío.

            Este método permite:
            - Controlar el acceso a los datos de forma centralizada y dinámica.
            - Modificar el comportamiento sin tocar código, cambiando únicamente las políticas de rol en el administrador de Django.
            - Mantener la lógica desacoplada de los nombres de grupos, usando la resolución de alcance (RoleScope) como única fuente de verdad.

            Parámetros:
                user (User): Usuario autenticado que realiza la consulta.
                queryset (QuerySet[T]): Conjunto base de datos sobre el cual se aplicará el filtro.

            Retorna:
                QuerySet[T]: El conjunto filtrado de acuerdo con el alcance del usuario.
            """
        scope = resolve_scope(user)

        if scope == RoleScope.ALL:
            return queryset
        elif scope == RoleScope.WORKCELL:
            return queryset.filter(project__work_cell__users=user)
        elif scope == RoleScope.OWNED:
            return queryset.filter(agent=user)
        else:
            return queryset.none()


    def get_base_queryset(self, user):
        optimized_clients = Prefetch(
            'contact__clients',
            queryset=Client.objects.select_related('city', 'business_group')
        )

        optimized_finance = Prefetch(
            'finance_data',
            queryset=Opportunity._meta.get_field('finance_data').related_model.objects.all()
        )

        optimized_documents = Prefetch(
            'documents',
            queryset=OpportunityDocument.objects.only(
                'id', 'file_name', 'sharepoint_url', 'uploaded_at', 'opportunity'
            )
        )

        queryset = Opportunity.objects.select_related(
            'status_opportunity',
            'currency',
            'opportunityType',
            'contact',
            'contact__job',
            'project',
            'project__specialty',
            'project__subdivision',
            'project__subdivision__division',
            'project__project_status',
            'project__work_cell',
            'project__work_cell__udn',
            'client',
            'client__city',
            'client__business_group'
        ).prefetch_related(
            optimized_finance,
            optimized_clients,
            optimized_documents
        )

        return self.add_filter_by_rol(user, queryset)


    def get_base_documents_queryset(self, user):
        optimized_clients = Prefetch(
            'opportunity__contact__clients',
            queryset=Client.objects.select_related('city', 'business_group')
        )

        optimized_finance = Prefetch(
            'opportunity__finance_data',
            queryset=Opportunity._meta.get_field('finance_data').related_model.objects.all()
        )

        queryset = OpportunityDocument.objects.select_related(
            'opportunity',
            'opportunity__status_opportunity',
            'opportunity__currency',
            'opportunity__opportunityType',
            'opportunity__contact',
            'opportunity__contact__job',
            'opportunity__project',
            'opportunity__project__specialty',
            'opportunity__project__subdivision',
            'opportunity__project__subdivision__division',
            'opportunity__project__project_status',
            'opportunity__project__work_cell',
            'opportunity__project__work_cell__udn',
            'opportunity__client',
            'opportunity__client__city',
            'opportunity__client__business_group'
        ).prefetch_related(
            optimized_finance,
            optimized_clients)

        return self.add_filter_by_rol(user, queryset)



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
                    oc_number=finance_data.get("oc_number", None)
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