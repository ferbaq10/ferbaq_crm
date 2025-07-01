from django.db import models
from django.conf import settings
from model_utils.models import SoftDeletableModel, TimeStampedModel


class BaseModel(SoftDeletableModel, TimeStampedModel):
    '''
    Para utilizar el manager del modelo para especificar que devuelva todos los datos aunuqe estén marcados
    como eliminados
    '''
    objects = models.Manager()

    all_objects = models.Manager()  # este sí devuelve todo

    class Meta:
        abstract = True  # <- Esto evita que Django lo trate como una tabla real


class UDN(BaseModel):
    name = models.CharField(
        unique=True,
        max_length=100,
        verbose_name="Nombre",
        error_messages={
            'unique': "Este nombre de UDN ya existe.",
            'max_length': "El nombre no puede exceder 100 caracteres."
        }
    )
    users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='udns',
        blank=True,
        verbose_name="Usuarios asignados"
    )

    class Meta:
        db_table = 'catalog_udns'
        verbose_name = "UDN"
        verbose_name_plural = "UDN's"
        ordering = ['-name']

    def __str__(self):
        return self.name

class WorkCell(BaseModel):
    name = models.CharField(
        unique=True,
        max_length=100,
        verbose_name="Nombre",
        error_messages={
            'unique': "Este nombre de célula de trabajo ya existe.",
            'max_length': "El nombre no puede exceder 100 caracteres."
        }
    )
    udn = models.ForeignKey(
        UDN,
        on_delete=models.DO_NOTHING,
        blank=True,
        null=True,
        verbose_name="UDN"
    )
    users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='workcell',
        blank=True,
        verbose_name="Usuarios asignados"
    )

    class Meta:
        db_table = 'catalog_work_cells'
        verbose_name = "Célula de trabajo"
        verbose_name_plural = "Células de trabajo"


    def __str__(self):
        return self.name

class BusinessGroup(BaseModel):
    name = models.CharField(
        unique=True,
        max_length=100,
        verbose_name="Nombre",
        error_messages={
            'unique': "Este grupo empresarial ya existe.",
            'max_length': "El nombre no puede exceder 100 caracteres."
        }
    )

    class Meta:
        db_table = 'catalog_business_groups'
        verbose_name = "Grupo empresarial"
        verbose_name_plural = "Grupos empresariales"

    def __str__(self):
        return self.name

class Division(BaseModel):
    name = models.CharField(
        unique=True,
        max_length=100,
        verbose_name="Nombre",
        error_messages={
            'unique': "Esta división ya existe.",
            'max_length': "El nombre no puede exceder 100 caracteres."
        }
    )
    business_group = models.ForeignKey(
        BusinessGroup,
        on_delete=models.DO_NOTHING,
        verbose_name="Grupo empresarial",
        blank=True,
        null=True
    )

    class Meta:
        db_table = 'catalog_divisions'
        verbose_name = "División"
        verbose_name_plural = "Divisiones"

    def __str__(self):
        return self.name

class Subdivision(BaseModel):
    name = models.CharField(
        unique=True,
        max_length=100,
        verbose_name="Nombre",
        error_messages={
            'unique': "Esta subdivisión ya existe.",
            'max_length': "El nombre no puede exceder 100 caracteres."
        }
    )
    division = models.ForeignKey(
        Division,
        on_delete=models.DO_NOTHING,
        verbose_name="División"
    )

    class Meta:
        db_table = 'catalog_subdivisions'
        verbose_name = "Subdivisión"
        verbose_name_plural = "Subdivisiones"

    def __str__(self):
        return self.name

class Specialty(BaseModel):
    name = models.CharField(
        unique=True,
        max_length=100,
        verbose_name="Nombre",
        error_messages={
            'unique': "Esta especialidad ya existe.",
            'max_length': "El nombre no puede exceder 100 caracteres."
        }
    )

    class Meta:
        db_table = 'catalog_specialities'
        verbose_name = "Especialidad"
        verbose_name_plural = "Especialidades"

    def __str__(self):
        return self.name

class Currency(BaseModel):
    name = models.CharField(
        unique=True,
        max_length=100,
        verbose_name="Nombre",
        error_messages={
            'unique': "Esta divisa ya existe.",
            'max_length': "El nombre no puede exceder 100 caracteres."
        }
    )

    class Meta:
        db_table = 'catalog_currencies'
        verbose_name = "Divisa"
        verbose_name_plural = "Divisas"

    def __str__(self):
        return self.name

class ProjectStatus(BaseModel):
    name = models.CharField(
        unique=True,
        max_length=100,
        verbose_name="Nombre",
        error_messages={
            'unique': "Este estado ya existe.",
            'max_length': "El nombre no puede exceder 100 caracteres."
        }
    )

    class Meta:
        db_table = 'catalog_project_status'
        verbose_name = "Estado del proyecto"
        verbose_name_plural = "Estados del proyecto"

    def __str__(self):
        return self.name

class City(BaseModel):
    name = models.CharField(
        unique=True,
        max_length=100,
        verbose_name="Nombre",
        error_messages={
            'unique': "Esta ciudad ya existe.",
            'max_length': "El nombre no puede exceder 100 caracteres."
        }
    )

    class Meta:
        db_table = 'catalog_cities'
        verbose_name = "Ciudad"
        verbose_name_plural = "Ciudades"

    def __str__(self):
        return self.name

class Period(BaseModel):
    name = models.CharField(
        unique=True,
        max_length=100,
        verbose_name="Nombre",
        error_messages={
            'unique': "Este período ya existe.",
            'max_length': "El nombre no puede exceder 100 caracteres."
        }
    )

    class Meta:
        db_table = 'catalog_periods'
        verbose_name = "Período"
        verbose_name_plural = "Períodos"

    def __str__(self):
        return self.name

class StatusOpportunity(BaseModel):
    name = models.CharField(
        unique=True,
        max_length=100,
        verbose_name="Nombre",
        error_messages={
            'unique': "Este estado de oportunidad ya existe.",
            'max_length': "El nombre no puede exceder 100 caracteres."
        }
    )

    class Meta:
        db_table = 'catalog_status_opportunities'
        verbose_name = "Estado de la oportunidad"
        verbose_name_plural = "Estados de la oportunidad"

    def __str__(self):
        return self.name

class Job(BaseModel):
    name = models.CharField(
        unique=True,
        max_length=100,
        verbose_name="Nombre",
        error_messages={
            'unique': "Este cargo ya existe.",
            'max_length': "El nombre no puede exceder 100 caracteres."
        }
    )

    class Meta:
        db_table = 'catalog_jobs'
        verbose_name = "Cargo"
        verbose_name_plural = "Cargos"

    def __str__(self):
        return self.name

class OpportunityType(BaseModel):
    name = models.CharField(
        unique=True,
        max_length=100,
        verbose_name="Nombre",
        error_messages={
            'unique': "Este tipo de oportunidad ya existe.",
            'max_length': "El nombre no puede exceder 100 caracteres."
        }
    )

    class Meta:
        db_table = 'catalog_opportunity_types'
        verbose_name = "Tipo de oportunidad"
        verbose_name_plural = "Tipo de oportunidades"

    def __str__(self):
        return self.name

class MeetingType(BaseModel):
    name = models.CharField(
        unique=True,
        max_length=100,
        verbose_name="Nombre",
        error_messages={
            'unique': "Este tipo de reunión ya existe.",
            'max_length': "El nombre no puede exceder 100 caracteres."
        }
    )


    class Meta:
        db_table = 'catalog_meeting_types'
        verbose_name = "Tipo de reunión"
        verbose_name_plural = "Tipo de reuniones"

    def __str__(self):
        return self.name

class MeetingResult(BaseModel):
    name = models.CharField(
        unique=True,
        max_length=100,
        verbose_name="Nombre",
        error_messages={
            'unique': "Este resultado de reunión ya existe.",
            'max_length': "El nombre no puede exceder 100 caracteres."
        }
    )


    class Meta:
        db_table = 'catalog_meeting_results'
        verbose_name = "Resultado de reunión"
        verbose_name_plural = "Resultado de reuniones"

    def __str__(self):
        return self.name

class LostOpportunityType(BaseModel):
    name = models.CharField(
        unique=True,
        max_length=100,
        verbose_name="Nombre",
        error_messages={
            'unique': "Este tipo de pérdida ya existe.",
            'max_length': "El nombre no puede exceder 100 caracteres."
        }
    )

    class Meta:
        db_table = 'catalog_lost_opportunity_type'
        verbose_name = "Tipo de pérdida de la oportunidad"
        verbose_name_plural = "Tipos de pérdidas de las oportunidades"

    def __str__(self):
        return self.name

class PurchaseStatusType(BaseModel):
    name = models.CharField(
        unique=True,
        max_length=100,
        verbose_name="Nombre",
        error_messages={
            'unique': "Este estado de compra ya existe.",
            'max_length': "El nombre no puede exceder 100 caracteres."
        }
    )

    class Meta:
        db_table = 'catalog_purchase_status'
        verbose_name = "Estado de la compra"
        verbose_name_plural = "Estados de la compra"

    def __str__(self):
        return self.name
