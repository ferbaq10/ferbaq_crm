from django.db import migrations

commercial_activities = [
    (1, "Llamada telefónica"),
    (2, "Visita"),
    (3, "Videollamada / Reunión virtual"),
    (4, "Envío de cotización"),
    (5, "Seguimiento a cotización"),
    (6, "Cierre de venta / Negociación"),
    (7, "Prospección de clientes"),
    (8, "Atención post-venta"),
    (9, "Llamada de seguimiento"),
    (10, "Registro en CRM"),
]

def insert_initial_commercial_activities(apps, schema_editor):
    CommercialActivity = apps.get_model('opportunity', 'CommercialActivity')
    for id_val, name in commercial_activities:
        CommercialActivity.objects.update_or_create(id=id_val, defaults={'name': name})

def remove_initial_commercial_activities(apps, schema_editor):
    CommercialActivity = apps.get_model('opportunity', 'CommercialActivity')
    names = [name for _, name in commercial_activities]
    CommercialActivity.objects.filter(name__in=names).delete()

class Migration(migrations.Migration):

    dependencies = [
        ('opportunity', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(insert_initial_commercial_activities,
                             reverse_code=remove_initial_commercial_activities)
    ]
