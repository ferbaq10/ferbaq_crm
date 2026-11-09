from django.db import migrations

STATUS_ID = 7
STATUS_NAME = "Por cerrar"


def add_por_cerrar(apps, schema_editor):
    """
    Crea la etapa 'Por cerrar' con id fijo 7 (el código usa ids fijos, ver
    catalog/constants.py). Es segura para correr en develop y producción:
    - si ya existe con ese nombre y id, no hace nada;
    - si el id 7 o el nombre ya los usa OTRA etapa, se detiene con un error claro
      para no pisar datos.
    """
    StatusOpportunity = apps.get_model('catalog', 'StatusOpportunity')
    manager = StatusOpportunity._base_manager  # incluye registros marcados como eliminados

    by_id = manager.filter(id=STATUS_ID).first()
    by_name = manager.filter(name=STATUS_NAME).first()

    if by_id and by_id.name == STATUS_NAME:
        if getattr(by_id, 'is_removed', False):
            by_id.is_removed = False
            by_id.save()
    elif by_id or by_name:
        raise RuntimeError(
            f"No se puede crear la etapa '{STATUS_NAME}' con id {STATUS_ID}: "
            f"ya existe id={getattr(by_id, 'id', None)} nombre={getattr(by_id, 'name', None)!r} / "
            f"nombre={'sí' if by_name else 'no'} (id {getattr(by_name, 'id', None)}). "
            f"Revisa catalog_status_opportunities antes de migrar."
        )
    else:
        StatusOpportunity.objects.create(id=STATUS_ID, name=STATUS_NAME)

    # El seed inserta ids a mano; en PostgreSQL hay que alinear la secuencia
    # para que un alta posterior desde el admin no choque con un id existente.
    if schema_editor.connection.vendor == 'postgresql':
        table = StatusOpportunity._meta.db_table
        schema_editor.execute(
            f"SELECT setval(pg_get_serial_sequence('{table}', 'id'), "
            f"(SELECT COALESCE(MAX(id), 1) FROM {table}))"
        )


def remove_por_cerrar(apps, schema_editor):
    StatusOpportunity = apps.get_model('catalog', 'StatusOpportunity')
    Opportunity = apps.get_model('opportunity', 'Opportunity')
    if Opportunity._base_manager.filter(status_opportunity_id=STATUS_ID).exists():
        raise RuntimeError(
            f"Hay oportunidades en '{STATUS_NAME}'. Muévelas a otra etapa antes de revertir."
        )
    StatusOpportunity._base_manager.filter(id=STATUS_ID, name=STATUS_NAME).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0003_create_roles_permissions_catalog'),
        ('opportunity', '0011_historicalopportunity_order_closing_date_and_more'),
    ]

    operations = [
        migrations.RunPython(add_por_cerrar, reverse_code=remove_por_cerrar),
    ]
