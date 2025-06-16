from django.db import models
from catalog.models import City, BusinessGroup, BaseModel
from model_utils.models import SoftDeletableModel, TimeStampedModel


class Client(BaseModel):
    rfc = models.CharField(
        unique=True,
        max_length=20,
        verbose_name="RFC"
    )
    company = models.CharField(
        unique=True,
        max_length=100,
        verbose_name="Razón social"
    )
    id_client = models.IntegerField(
        unique=True,
        verbose_name="Id de cliente"
    )
    city = models.ForeignKey(
        City,
        on_delete=models.DO_NOTHING,
        blank=True,
        null=True,
        verbose_name="Ciudad"
    )
    business_group = models.ForeignKey(
        BusinessGroup,
        blank=True,
        on_delete=models.DO_NOTHING,
        verbose_name="Grupo empresarial"
    )

    class Meta:
        db_table = 'client_clients'
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"

    def __str__(self):
        return self.company

