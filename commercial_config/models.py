from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from simple_history.models import HistoricalRecords

from catalog.models import (
    BaseModel,
    City,
    UDN,
    WorkCell,
)
from client.models import Client
from contact.models import Contact
from project.models import Project


class DeliverySite(BaseModel):
    """
    Sitio físico de entrega asociado a uno o varios
    centros de costo.

    Ejemplos:
    - Los Mochis
    - Monterrey
    - Querétaro
    - México Centro
    """

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
        City,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name='delivery_sites',
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
        ordering = [
            'name',
        ]

    def __str__(self):
        return self.name


class CostCenter(BaseModel):
    """
    Centro de costo maestro.

    Contiene la configuración financiera y logística
    predeterminada que posteriormente heredará el pedido.
    """

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
        Contact,
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
        ordering = [
            'code',
        ]

    def __str__(self):
        if self.name:
            return f'{self.code} - {self.name}'

        return self.code


class ClientProjectConfiguration(BaseModel):
    """
    Configuración maestra de una combinación
    Cliente + Proyecto.

    Esta será la fuente de verdad para determinar:
    - UDN
    - Centro de costo
    - Centro de costo del cliente
    - Célula opcional

    La combinación Cliente + Proyecto debe tener una sola
    configuración vigente.
    """

    class ValidationStatus(models.TextChoices):
        PENDING = (
            'PENDING',
            'Pendiente de validación',
        )
        APPROVED = (
            'APPROVED',
            'Aprobada',
        )
        REJECTED = (
            'REJECTED',
            'Rechazada',
        )

    client = models.ForeignKey(
        Client,
        on_delete=models.PROTECT,
        related_name='project_configurations',
        verbose_name='Cliente',
    )

    project = models.ForeignKey(
        Project,
        on_delete=models.PROTECT,
        related_name='client_configurations',
        verbose_name='Proyecto',
    )

    udn = models.ForeignKey(
        UDN,
        on_delete=models.PROTECT,
        related_name='client_project_configurations',
        verbose_name='UDN',
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

    work_cell = models.ForeignKey(
        WorkCell,
        on_delete=models.PROTECT,
        related_name='client_project_configurations',
        blank=True,
        null=True,
        verbose_name='Célula de trabajo',
        help_text=(
            'Dato comercial opcional. '
            'La UDN es la dimensión operativa principal.'
        ),
    )

    validation_status = models.CharField(
        max_length=20,
        choices=ValidationStatus.choices,
        default=ValidationStatus.PENDING,
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
        ]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    'client',
                    'project',
                ],
                condition=Q(
                    is_removed=False
                ),
                name=(
                    'unique_active_client_project_config'
                ),
            ),
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

    def clean(self):
        super().clean()

        # -------------------------------------------------
        # El proyecto debe pertenecer al cliente.
        # -------------------------------------------------

        if (
            self.client_id
            and self.project_id
        ):
            pertenece = (
                self.client.projects
                .filter(
                    pk=self.project_id
                )
                .exists()
            )

            if not pertenece:
                raise ValidationError({
                    'project': (
                        'El proyecto seleccionado no está '
                        'asociado al cliente seleccionado.'
                    ),
                })

        # -------------------------------------------------
        # Si existe célula, debe pertenecer a la misma UDN.
        # -------------------------------------------------

        if (
            self.work_cell_id
            and self.udn_id
            and self.work_cell.udn_id
            != self.udn_id
        ):
            raise ValidationError({
                'work_cell': (
                    'La célula seleccionada pertenece '
                    'a una UDN diferente.'
                ),
            })

    def __str__(self):
        return (
            f'{self.client.company} - '
            f'{self.project.name} - '
            f'{self.cost_center.code}'
        )