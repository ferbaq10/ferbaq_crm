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

lost_opportunity_types = [
    (1, "Precio muy alto para el cliente"),
    (2, "El cliente no tenía presupuesto"),
    (3, "El competidor ofreció mejor precio"),
    (4, "Oportunidad ganada por un competidor"),
    (5, "Competidor ya tenía relación previa"),
    (6, "Mejor oferta de valor del competidor"),
    (7, "Cliente se quedó con proveedor actual"),
    (8, "No se justificó el valor por el costo"),
    (9, "No cubre necesidades del cliente"),
    (10, "Falta de funcionalidades o personalización"),
    (11, "Problemas de compatibilidad"),
    (12, "Producto/servicio en desarrollo o sin disponibilidad"),
    (13, "Falta de seguimiento oportuno"),
    (14, "Mala experiencia en el proceso comercial"),
    (15, "Retraso en la cotización o respuesta"),
    (16, "Comunicación deficiente del ejecutivo"),
    (17, "Proyecto cancelado o pausado"),
    (18, "Cambio de prioridades internas"),
    (19, "Cambio en el equipo decisor"),
    (20, "Cliente decidió no hacer nada"),
    (20, "Propuesta entregada fuera de tiempo"),
    (21, "Cliente requería entrega inmediata"),
    (22, "Nuestro tiempo de implementación era muy largo"),
    (23, "Formas de pago no aceptadas"),
    (24, "Condiciones de entrega inadecuadas"),
    (25, "Requieren financiamiento o crédito"),
    (26, "Sin stock o sin capacidad operativa"),
    (27, "Problemas logísticos"),
    (28, "Demora en la producción"),
    (29, "Cliente no dio razón específica"),
    (30, "Información insuficiente para clasificar"),
    (31, "Error interno (cotización mal enviada, etc.)"),
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
        ('opportunity', '0002_create_roles_permissions_opportunity'),
    ]

    operations = [
        migrations.RunPython(insert_initial_commercial_activities,
                             reverse_code=remove_initial_commercial_activities)
    ]
