from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from catalog.models import UDN
from client.models import Client
from project.models import Project

from commercial_config.models import (
    ClientProjectConfiguration,
    CostCenter,
    DeliverySite,
)


class Command(BaseCommand):
    help = (
        'Crea o actualiza las configuraciones piloto '
        'de Noroeste y Centro.'
    )

    def handle(self, *args, **options):
        pilotos = [
            {
                'nombre': 'Noroeste',
                'client_id': 52,
                'client_name': 'Bonatti Mexico',
                'project_id': 78,
                'project_name': 'ECA LNG',
                'udn_name': 'Noroeste',
                'site_code': 'PILOT_NOR',
                'site_name': 'Sitio Piloto Noroeste',
                'cost_center_code': 'CC_PILOT_NOR',
                'cost_center_name': (
                    'Centro de Costo Piloto Noroeste'
                ),
                'credit_days': 30,
            },
            {
                'nombre': 'Centro',
                'client_id': 18,
                'client_name': 'ATC Altamira III Y IV',
                'project_id': 37,
                'project_name': 'Central Electrica Altamira',
                'udn_name': 'Centro',
                'site_code': 'PILOT_CEN',
                'site_name': 'Sitio Piloto Centro',
                'cost_center_code': 'CC_PILOT_CEN',
                'cost_center_name': (
                    'Centro de Costo Piloto Centro'
                ),
                'credit_days': 30,
            },
        ]

        self.stdout.write('')
        self.stdout.write(
            '========================================'
        )
        self.stdout.write(
            'CONFIGURACIÓN PILOTO COMERCIAL'
        )
        self.stdout.write(
            '========================================'
        )

        for datos in pilotos:
            try:
                # Cada piloto es una unidad atómica.
                #
                # Si cualquier validación o escritura falla,
                # se revierte:
                #
                # DeliverySite
                # CostCenter
                # ClientProjectConfiguration
                #
                # de ese piloto.
                with transaction.atomic():
                    self._crear_piloto(datos)

            except Exception as error:
                raise CommandError(
                    f"Error creando piloto "
                    f"{datos['nombre']}: {error}"
                ) from error

        self.stdout.write('')
        self.stdout.write(
            self.style.SUCCESS(
                '✅ CONFIGURACIÓN PILOTO COMPLETADA'
            )
        )

    def _crear_piloto(self, datos):
        self.stdout.write('')
        self.stdout.write(
            f"--- {datos['nombre']} ---"
        )

        # ==================================================
        # CLIENTE
        # ==================================================

        try:
            client = Client.objects.get(
                pk=datos['client_id'],
                is_removed=False,
            )
        except Client.DoesNotExist as error:
            raise CommandError(
                'No existe el cliente '
                f"{datos['client_id']}"
            ) from error

        if client.company.strip() != datos['client_name']:
            raise CommandError(
                'El cliente encontrado no coincide. '
                f"Esperado={datos['client_name']!r}, "
                f"encontrado={client.company!r}, "
                f"id={client.pk}"
            )

        # ==================================================
        # PROYECTO
        # ==================================================

        try:
            project = Project.objects.select_related(
                'work_cell',
                'work_cell__udn',
            ).get(
                pk=datos['project_id'],
                is_removed=False,
            )
        except Project.DoesNotExist as error:
            raise CommandError(
                'No existe el proyecto '
                f"{datos['project_id']}"
            ) from error

        if project.name.strip() != datos['project_name']:
            raise CommandError(
                'El proyecto encontrado no coincide. '
                f"Esperado={datos['project_name']!r}, "
                f"encontrado={project.name!r}, "
                f"id={project.pk}"
            )

        # ==================================================
        # CLIENTE ↔ PROYECTO
        # ==================================================

        if not client.projects.filter(
            pk=project.pk
        ).exists():
            raise CommandError(
                f'El cliente {client.company!r} '
                f'no está relacionado con el proyecto '
                f'{project.name!r}.'
            )

        # ==================================================
        # UDN
        # ==================================================

        try:
            udn = UDN.objects.get(
                name__iexact=datos['udn_name'],
                is_removed=False,
            )
        except UDN.DoesNotExist as error:
            raise CommandError(
                'No existe la UDN '
                f"{datos['udn_name']!r}"
            ) from error

        # ==================================================
        # WORK CELL
        # ==================================================

        work_cell = getattr(
            project,
            'work_cell',
            None,
        )

        # Para este piloto también verificamos que
        # la célula actual del proyecto coincida
        # con la UDN que queremos configurar.
        #
        # OJO:
        # Esto es únicamente una validación del piloto.
        # La fuente operativa final seguirá siendo:
        #
        # Client + Project
        #       ↓
        # ClientProjectConfiguration
        #       ↓
        # UDN
        #
        if work_cell is not None:
            work_cell_udn = getattr(
                work_cell,
                'udn',
                None,
            )

            if (
                work_cell_udn is not None
                and work_cell_udn.pk != udn.pk
            ):
                raise CommandError(
                    f'La célula {work_cell.name!r} '
                    f'pertenece a UDN '
                    f'{work_cell_udn.name!r}, '
                    f'pero el piloto intenta asignar '
                    f'{udn.name!r}.'
                )

        # ==================================================
        # SITIO DE ENTREGA
        # ==================================================

        delivery_site, site_created = (
            DeliverySite.objects.update_or_create(
                code=datos['site_code'],
                defaults={
                    'name': datos['site_name'],
                    'address': None,
                    'postal_code': None,
                    'notes': (
                        'Registro temporal utilizado '
                        'para el piloto end-to-end '
                        'de configuración comercial.'
                    ),
                    'is_active': True,
                    'is_removed': False,
                },
            )
        )

        # ==================================================
        # CENTRO DE COSTO
        # ==================================================

        cost_center, cc_created = (
            CostCenter.objects.update_or_create(
                code=datos['cost_center_code'],
                defaults={
                    'name': (
                        datos['cost_center_name']
                    ),
                    'delivery_site': delivery_site,
                    'default_credit_days': (
                        datos['credit_days']
                    ),
                    'collection_contact': None,
                    'notes': (
                        'Centro de costo temporal '
                        'utilizado para el piloto '
                        'end-to-end.'
                    ),
                    'is_active': True,
                    'is_removed': False,
                },
            )
        )

        # ==================================================
        # CONFIGURACIÓN CLIENTE + PROYECTO
        # ==================================================
        #
        # NO usamos update_or_create() aquí.
        #
        # Primero construimos/modificamos el objeto
        # en memoria.
        #
        # Después ejecutamos full_clean().
        #
        # Solamente si pasa las validaciones hacemos save().
        #
        # Además, todo está dentro de transaction.atomic().
        # Si algo falla, también se revierten sitio y CC.
        # ==================================================

        configuration = (
            ClientProjectConfiguration.objects
            .select_for_update()
            .filter(
                client=client,
                project=project,
                is_removed=False,
            )
            .first()
        )

        config_created = configuration is None

        if configuration is None:
            configuration = ClientProjectConfiguration(
                client=client,
                project=project,
            )

        configuration.udn = udn
        configuration.cost_center = cost_center
        configuration.client_cost_center = None
        configuration.work_cell = work_cell

        configuration.validation_status = (
            ClientProjectConfiguration
            .ValidationStatus
            .APPROVED
        )

        configuration.validated_at = timezone.now()

        configuration.validated_by_username = (
            'pilot_setup'
        )

        configuration.validation_comment = (
            'Configuración aprobada temporalmente '
            'para pruebas end-to-end.'
        )

        configuration.is_active = True
        configuration.is_removed = False

        # ==================================================
        # VALIDAR ANTES DE GUARDAR
        # ==================================================

        configuration.full_clean()

        # ==================================================
        # GUARDAR SOLO SI PASÓ VALIDACIONES
        # ==================================================

        configuration.save()

        # ==================================================
        # SALIDA
        # ==================================================

        self.stdout.write(
            f'Cliente: {client.company}'
        )

        self.stdout.write(
            f'Proyecto: {project.name}'
        )

        self.stdout.write(
            f'UDN: {udn.name}'
        )

        self.stdout.write(
            'Célula: '
            f'{work_cell.name if work_cell else "-"}'
        )

        self.stdout.write(
            'Sitio: '
            f'{delivery_site.code} - '
            f'{delivery_site.name}'
        )

        self.stdout.write(
            'Centro costo: '
            f'{cost_center.code} - '
            f'{cost_center.name}'
        )

        self.stdout.write(
            'Días crédito: '
            f'{cost_center.default_credit_days}'
        )

        self.stdout.write(
            'Validación: '
            f'{configuration.validation_status}'
        )

        self.stdout.write(
            'Validado por: '
            f'{configuration.validated_by_username}'
        )

        self.stdout.write(
            'IDs: '
            f'sitio={delivery_site.pk}, '
            f'cc={cost_center.pk}, '
            f'config={configuration.pk}'
        )

        self.stdout.write(
            'Resultado: '
            f'sitio='
            f'{"CREADO" if site_created else "ACTUALIZADO"}, '
            f'cc='
            f'{"CREADO" if cc_created else "ACTUALIZADO"}, '
            f'config='
            f'{"CREADA" if config_created else "ACTUALIZADA"}'
        )