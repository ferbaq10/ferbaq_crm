from django.core.exceptions import ValidationError
from django.db import models
from simple_history.models import HistoricalRecords

from catalog.models import BaseModel


class DeliverySite(BaseModel):
    code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Código',
    )

    name = models.CharField(
        max_length=150,
        unique=True,
        verbose_name='Nombre',
    )

    address = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='Dirección',
    )

    city = models.ForeignKey(
        'catalog.City',
        on_delete=models.PROTECT,
        related_name='delivery_sites',
        blank=True,
        null=True,
        verbose_name='Ciudad',
    )

    postal_code = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        verbose_name='Código postal',
    )

    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name='Notas',
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name='Activo',
    )

    history = HistoricalRecords()

    class Meta:
        db_table = 'commercial_delivery_sites'
        verbose_name = 'Sitio de entrega'
        verbose_name_plural = 'Sitios de entrega'
        ordering = ['name']

    def __str__(self):
        return f'{self.code} - {self.name}'


class CostCenter(BaseModel):
    code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Código',
    )

    name = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        verbose_name='Nombre descriptivo',
    )

    delivery_site = models.ForeignKey(
        DeliverySite,
        on_delete=models.PROTECT,
        related_name='cost_centers',
        verbose_name='Sitio de entrega',
    )

    default_credit_days = models.PositiveSmallIntegerField(
        verbose_name='Días de crédito predeterminados',
        help_text=(
            'Días de crédito que se propondrán por defecto '
            'cuando una factura llegue a Crédito y Cobranza.'
        ),
    )

    collection_contact = models.ForeignKey(
        'contact.Contact',
        on_delete=models.PROTECT,
        related_name='collection_cost_centers',
        blank=True,
        null=True,
        verbose_name='Contacto de cobranza',
    )

    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name='Notas',
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name='Activo',
    )

    history = HistoricalRecords()

    class Meta:
        db_table = 'commercial_cost_centers'
        verbose_name = 'Centro de costo'
        verbose_name_plural = 'Centros de costo'
        ordering = ['code']

    def __str__(self):
        if self.name:
            return f'{self.code} - {self.name}'

        return self.code


class ClientProjectConfiguration(BaseModel):
    VALIDATION_PENDING = 'PENDING'
    VALIDATION_APPROVED = 'APPROVED'
    VALIDATION_REJECTED = 'REJECTED'

    VALIDATION_STATUS_CHOICES = [
        (
            VALIDATION_PENDING,
            'Pendiente de validación',
        ),
        (
            VALIDATION_APPROVED,
            'Aprobada',
        ),
        (
            VALIDATION_REJECTED,
            'Rechazada',
        ),
    ]

    client = models.ForeignKey(
        'client.Client',
        on_delete=models.PROTECT,
        related_name='project_configurations',
        verbose_name='Cliente',
    )

    project = models.ForeignKey(
        'project.Project',
        on_delete=models.PROTECT,
        related_name='client_configurations',
        verbose_name='Proyecto',
    )

    cost_center = models.ForeignKey(
        CostCenter,
        on_delete=models.PROTECT,
        related_name='client_project_configurations',
        verbose_name='Centro de costo',
    )

    client_cost_center = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        verbose_name='Centro de costo del cliente',
        help_text=(
            'Código o descripción que el cliente utiliza '
            'internamente. Es opcional.'
        ),
    )

    # ==========================================================
    # CAMPOS LEGADO
    # ==========================================================
    #
    # Se conservan temporalmente porque Portal FERBAQ todavía
    # los consume.
    #
    # La nueva fuente operativa serán ClientProjectRoute
    # y ClientProjectRouteWorkCell.
    #
    # NO deben usarse para nuevas reglas de negocio.
    # ==========================================================

    udn = models.ForeignKey(
        'catalog.UDN',
        on_delete=models.PROTECT,
        related_name='client_project_configurations',
        blank=True,
        null=True,
        verbose_name='UDN legado',
        help_text=(
            'Campo legado. La UDN operativa debe obtenerse '
            'de las rutas de la configuración.'
        ),
    )

    work_cell = models.ForeignKey(
        'catalog.WorkCell',
        on_delete=models.PROTECT,
        related_name='client_project_configurations',
        blank=True,
        null=True,
        verbose_name='Célula legado',
        help_text=(
            'Campo legado. La visibilidad comercial debe '
            'obtenerse de las células autorizadas de cada ruta.'
        ),
    )

    validation_status = models.CharField(
        max_length=20,
        choices=VALIDATION_STATUS_CHOICES,
        default=VALIDATION_PENDING,
        verbose_name='Estatus de validación',
    )

    validated_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Validado en',
    )

    validated_by_username = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        verbose_name='Validado por',
    )

    validation_comment = models.TextField(
        blank=True,
        null=True,
        verbose_name='Comentario de validación',
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name='Activo',
    )

    history = HistoricalRecords()

    class Meta:
        db_table = (
            'commercial_client_project_configurations'
        )

        verbose_name = (
            'Configuración de cliente y proyecto'
        )

        verbose_name_plural = (
            'Configuraciones de clientes y proyectos'
        )

        ordering = [
            'client__company',
            'project__name',
            'cost_center__code',
        ]

        indexes = [
            models.Index(
                fields=[
                    'validation_status',
                    'is_active',
                ],
                name='idx_cfg_validation_active',
            ),
            models.Index(
                fields=[
                    'client',
                    'project',
                ],
                name='idx_cfg_client_project',
            ),
        ]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    'client',
                    'project',
                    'cost_center',
                ],
                condition=models.Q(
                    is_removed=False,
                ),
                name='uniq_active_cfg_client_project_cc',
            ),
        ]

    def clean(self):
        super().clean()

        if (
            self.client_id
            and self.project_id
        ):
            pertenece = (
                self.client.projects
                .filter(
                    pk=self.project_id,
                )
                .exists()
            )

            if not pertenece:
                raise ValidationError({
                    'project': (
                        'El proyecto seleccionado no pertenece '
                        'al cliente seleccionado.'
                    ),
                })

    def __str__(self):
        return (
            f'{self.client} / '
            f'{self.project} / '
            f'{self.cost_center}'
        )


class ClientProjectRoute(BaseModel):
    """
    Ruta operativa válida para una configuración comercial.

    Una misma configuración Cliente + Proyecto + Centro de costo
    puede operar por varias UDN.
    """

    configuration = models.ForeignKey(
        ClientProjectConfiguration,
        on_delete=models.PROTECT,
        related_name='routes',
        verbose_name='Configuración comercial',
    )

    udn = models.ForeignKey(
        'catalog.UDN',
        on_delete=models.PROTECT,
        related_name='commercial_routes',
        verbose_name='UDN',
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name='Activa',
    )

    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name='Notas',
    )

    history = HistoricalRecords()

    class Meta:
        db_table = 'commercial_client_project_routes'

        verbose_name = 'Ruta comercial'
        verbose_name_plural = 'Rutas comerciales'

        ordering = [
            'configuration_id',
            'udn__name',
        ]

        indexes = [
            models.Index(
                fields=[
                    'configuration',
                    'is_active',
                ],
                name='idx_route_cfg_active',
            ),
            models.Index(
                fields=[
                    'udn',
                    'is_active',
                ],
                name='idx_route_udn_active',
            ),
        ]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    'configuration',
                    'udn',
                ],
                condition=models.Q(
                    is_removed=False,
                ),
                name='uniq_active_cfg_udn_route',
            ),
        ]

    def __str__(self):
        return (
            f'{self.configuration} / '
            f'{self.udn}'
        )


class ClientProjectRouteWorkCell(BaseModel):
    """
    Célula comercial autorizada para utilizar una ruta.

    Importante:
    la célula NO necesita pertenecer a la misma UDN de la ruta.

    Ejemplo:
    Célula 3 puede estar autorizada tanto para Centro
    como para Noroeste.
    """

    route = models.ForeignKey(
        ClientProjectRoute,
        on_delete=models.PROTECT,
        related_name='work_cell_assignments',
        verbose_name='Ruta comercial',
    )

    work_cell = models.ForeignKey(
        'catalog.WorkCell',
        on_delete=models.PROTECT,
        related_name='commercial_route_assignments',
        verbose_name='Célula autorizada',
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name='Activa',
    )

    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name='Notas',
    )

    history = HistoricalRecords()

    class Meta:
        db_table = (
            'commercial_client_project_route_work_cells'
        )

        verbose_name = (
            'Célula autorizada para ruta comercial'
        )

        verbose_name_plural = (
            'Células autorizadas para rutas comerciales'
        )

        ordering = [
            'route_id',
            'work_cell__name',
        ]

        indexes = [
            models.Index(
                fields=[
                    'route',
                    'is_active',
                ],
                name='idx_route_cell_active',
            ),
            models.Index(
                fields=[
                    'work_cell',
                    'is_active',
                ],
                name='idx_cell_route_active',
            ),
        ]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    'route',
                    'work_cell',
                ],
                condition=models.Q(
                    is_removed=False,
                ),
                name='uniq_active_route_work_cell',
            ),
        ]

    def __str__(self):
        return (
            f'{self.route} / '
            f'{self.work_cell}'
        )