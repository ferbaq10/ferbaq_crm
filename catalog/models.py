from django.db import models
from django.conf import settings

class UDN(models.Model):
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

    def __str__(self):
        return self.name


class WorkCell(models.Model):
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


class BusinessGroup(models.Model):
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


class Division(models.Model):
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
        verbose_name="Grupo empresarial"
    )

    class Meta:
        db_table = 'catalog_divisions'
        verbose_name = "División"
        verbose_name_plural = "Divisiones"

    def __str__(self):
        return self.name


class Subdivision(models.Model):
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


class Speciality(models.Model):
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


class ProjectStatus(models.Model):
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


class City(models.Model):
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
        db_table = 'catalog_city'
        verbose_name = "Ciudad"
        verbose_name_plural = "Ciudades"

    def __str__(self):
        return self.name


class Period(models.Model):
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


class StatusOpportunity(models.Model):
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