from django.db import migrations
from django.db import connection


periods = [
    "Primer Trimestre",
    "Segundo Trimestre",
    "Tercer Trimestre",
    "Cuarto Trimestre",
    "Anual",
    "Mensual"
]

cities = [
    "Mexicali",
    "Monterrey",
    "Merida",
    "Tijuana",
    "Chihuahua",
    "Mx",
    "Queretaro",
]

udns = [
    (1, "Centro"),
    (2, "Noroeste"),
    (3, "Sureste"),
]

business_groups = [
    (1, "Bonatti"),
    (2, "ICA"),
    (3, "Grupo México"),
    (4, "Carso"),
    (5, "Veolia"),
]

divisions = [
    (1, "Agua"),
    (2, "Energía"),
    (3, "Transporte"),
]

subdivisions = [
    (1, "Marítima", 1),
    (2, "Eólica", 2),
    (3, "Fotovoltáica", 2),
]

specialties = [
    (1, "EPC"),
    (2, "MRO"),
]

currencies = [
    (1, "MN"),
    (2, "USD"),
]

project_statuses = [
    (1, "Prospecto"),
    (2, "Activo"),
]

status_opportunities = [
    (1, "Sin cotizar"),
    (2, "Cotizando"),
    (3, "Oferta enviada"),
    (4, "Negociando"),
    (5, "Ganada"),
    (6, "Perdida"),
]

jobs = [
    (1, "Auxiliar de compras"),
    (2, "Comprador Jr."),
    (3, "Comprador Sr."),
    (4, "Analista de compras"),
    (5, "Coordinador de compras"),
    (6, "Jefe de compras"),
    (7, "Gerente de compras"),
    (8, "Director de compras"),
]

opportunity_types = [
    (1, "Ordinaria"),
    (2, "Licitación ITP"),
    (3, "Licitación AD"),
    (4, "Contrato general"),
    (5, "Contrato marco"),
    (6, "Estudio de mercado")
]

meeting_types = [
    (1, "Comida de negocios"),
    (2, "Visita comercial a corporativo"),
    (3, "Visita comercial a usuario final"),
    (4, "Visita comercial a proyecto"),
    (5, "Visita técnica - usuario final"),
    (6, "Demostración o capacitación"),
    (7, "Apertura de ofertas - licitación"),
    (8, "Entrega de presentes"),
    (9, "Prospección con cita"),
    (10, "Prospección en frio"),
]

meeting_results = [
    (1, "Cierre de orden de compra"),
    (2, "Homologación de producto o marca"),
    (3, "Fortalecimiento de la relación"),
    (4, "Cierre de contrato general / marco"),
    (5, "Obtención de información clave"),
    (6, "Detección de nuevos proyectos")
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

purchase_status_type = [
    (1, "Pendiente"),
    (2, "En proceso"),
    (3, "Esperando retroalimentación"),
    (4, "Parcial"),
    (5, "Finalizada"),
    (6, "Rechazada")
]




# --- Inserciones ---
def insert_initial_periods(apps, schema_editor):
    Period = apps.get_model('catalog', 'Period')
    for name in periods:
        Period.objects.update_or_create(name=name)

def insert_initial_cities(apps, schema_editor):
    City = apps.get_model('catalog', 'City')
    for name in cities:
        City.objects.update_or_create(name=name)

def insert_initial_udns(apps, schema_editor):
    UDN = apps.get_model('catalog', 'UDN')
    for id_val, name in udns:
        UDN.objects.update_or_create(id=id_val, defaults={'name': name})

def insert_initial_business_groups(apps, schema_editor):
    BusinessGroup = apps.get_model('catalog', 'BusinessGroup')
    for id_val, name in business_groups:
        BusinessGroup.objects.update_or_create(id=id_val, defaults={'name': name})

def insert_initial_divisions(apps, schema_editor):
    Division = apps.get_model('catalog', 'Division')
    for id_val, name in divisions:
        Division.objects.update_or_create(id=id_val, defaults={'name': name})

def insert_initial_subdivisions(apps, schema_editor):
    Subdivision = apps.get_model('catalog', 'Subdivision')
    Division = apps.get_model('catalog', 'Division')
    for id_val, name, division_id in subdivisions:
        division = Division.objects.get(id=division_id)
        Subdivision.objects.update_or_create(id=id_val, defaults={'name': name, 'division': division})

def insert_initial_specialties(apps, schema_editor):
    Specialty = apps.get_model('catalog', 'Specialty')
    for id_val, name in specialties:
        Specialty.objects.update_or_create(id=id_val, defaults={'name': name})

def insert_initial_project_statuses(apps, schema_editor):
    ProjectStatus = apps.get_model('catalog', 'ProjectStatus')
    for id_val, name in project_statuses:
        ProjectStatus.objects.update_or_create(id=id_val, defaults={'name': name})

def insert_initial_status_opportunities(apps, schema_editor):
    StatusOpportunity = apps.get_model('catalog', 'StatusOpportunity')
    for id_val, name in status_opportunities:
        StatusOpportunity.objects.update_or_create(id=id_val, defaults={'name': name})

def insert_initial_currencies(apps, schema_editor):
    Currency = apps.get_model('catalog', 'Currency')
    for id_val, name in currencies:
        Currency.objects.update_or_create(id=id_val, defaults={'name': name})

def insert_initial_jobs(apps, schema_editor):
    Job = apps.get_model('catalog', 'job')
    for id_val, name in jobs:
        Job.objects.update_or_create(id=id_val, defaults={'name': name})

def insert_initial_opportunity_types(apps, schema_editor):
    OpportunityType = apps.get_model('catalog', 'OpportunityType')
    for id_val, name in opportunity_types:
        OpportunityType.objects.update_or_create(id=id_val, defaults={'name': name})

def insert_initial_meeting_types(apps, schema_editor):
    MeetingType = apps.get_model('catalog', 'MeetingType')
    for id_val, name in meeting_types:
        MeetingType.objects.update_or_create(id=id_val, defaults={'name': name})

def insert_initial_meeting_results(apps, schema_editor):
    MeetingResult = apps.get_model('catalog', 'MeetingResult')
    for id_val, name in meeting_results:
        MeetingResult.objects.update_or_create(id=id_val, defaults={'name': name})


def insert_initial_lost_opportunity_type(apps, schema_editor):
    LostOpportunityType = apps.get_model('catalog', 'LostOpportunityType')
    for id_val, name in lost_opportunity_types:
        LostOpportunityType.objects.update_or_create(id=id_val, defaults={'name': name})


def insert_initial_purchase_status_type(apps, schema_editor):
    PurchaseStatusType = apps.get_model('catalog', 'PurchaseStatusType')
    for id_val, name in purchase_status_type:
        PurchaseStatusType.objects.update_or_create(id=id_val, defaults={'name': name})



# --- Eliminaciones ---
def bulk_delete(model, ids):
    model.objects.filter(id__in=ids).delete()

def remove_initial_periods(apps, schema_editor):
    Period = apps.get_model('catalog', 'Period')
    Period.objects.filter(name__in=periods).delete()

def remove_initial_cities(apps, schema_editor):
    City = apps.get_model('catalog', 'City')
    City.objects.filter(name__in=cities).delete()

def remove_initial_udns(apps, schema_editor):
    UDN = apps.get_model('catalog', 'UDN')
    WorkCell = apps.get_model('catalog', 'WorkCell')

    # Obtener IDs de las UDNs que quieres eliminar
    udn_ids = list(
        UDN.objects.filter(name__in=[name for _, name in udns])
        .values_list('id', flat=True)
    )

    # Eliminar primero las WorkCell que dependen de esas UDNs
    bulk_delete(WorkCell, ids=[
        wc_id for wc_id in WorkCell.objects.filter(udn_id__in=udn_ids).values_list('id', flat=True)
    ])

    # Luego eliminar las UDNs
    bulk_delete(UDN, ids=udn_ids)

def remove_initial_business_groups(apps, schema_editor):
    BusinessGroup = apps.get_model('catalog', 'BusinessGroup')
    BusinessGroup.objects.filter(name__in=[name for _, name in business_groups]).delete()

def remove_initial_divisions(apps, schema_editor):
    Division = apps.get_model('catalog', 'Division')
    Division.objects.filter(name__in=[name for _, name in divisions]).delete()

def remove_initial_subdivisions(apps, schema_editor):
    Division = apps.get_model('catalog', 'Division')
    Subdivision = apps.get_model('catalog', 'Subdivision')
    Project = apps.get_model('project', 'Project')

    # Buscar o crear una Division segura
    default_division = Division.objects.filter(name="Desconocida").first()
    if not default_division:
        default_division = Division.objects.create(name="Desconocida")

    # Buscar o crear una Subdivision segura con esa Division
    default_subdivision = Subdivision.objects.filter(name="Desconocida").first()
    if not default_subdivision:
        default_subdivision = Subdivision.objects.create(
            name="Desconocida",
            division=default_division
        )

    # Reasignar proyectos que apunten a subdivisiones a eliminar
    initial_subdivision_names = [name for name in subdivisions]
    Project.objects.filter(
        subdivision__name__in=initial_subdivision_names
    ).update(subdivision=default_subdivision)

    # Eliminar las subdivisiones iniciales (excepto la de fallback)
    Subdivision.objects.filter(
        name__in=initial_subdivision_names
    ).exclude(id=default_subdivision.id).delete()

def remove_initial_specialties(apps, schema_editor):
    Specialty = apps.get_model('catalog', 'Specialty')
    Project = apps.get_model('project', 'Project')

    # Buscar o crear una especialidad "Desconocida"
    default_speciality = Specialty.objects.filter(name="Desconocida").first()
    if not default_speciality:
        default_speciality = Specialty.objects.create(name="Desconocida")

    # Reasignar todos los proyectos que usaban las especialidades a borrar
    Project.objects.filter(
        specialty_id__in=[1]  # IDs que quieras eliminar
    ).update(specialty=default_speciality)

    # Ahora sí puedes eliminar
    Specialty.objects.filter(id__in=[1]).exclude(id=default_speciality.id).delete()

    # Sincronizar la secuencia
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT setval(
                pg_get_serial_sequence('catalog_specialities', 'id'),
                COALESCE((SELECT MAX(id) FROM catalog_specialities), 1)
            );
        """)

def remove_initial_project_statuses(apps, schema_editor):
    StatusOpportunity = apps.get_model('catalog', 'StatusOpportunity')
    StatusOpportunity.objects.filter(name__in=[name for _, name in status_opportunities]).delete()

def remove_initial_status_opportunities(apps, schema_editor):
    StatusOpportunity = apps.get_model('catalog', 'StatusOpportunity')
    StatusOpportunity.objects.filter(name__in=[name for _, name in status_opportunities]).delete()

def remove_initial_currencies(apps, schema_editor):
    Currency = apps.get_model('catalog', 'Currency')
    Currency.objects.filter(name__in=[name for _, name in currencies]).delete()

def remove_initial_job(apps, schema_editor):
    Job = apps.get_model('catalog', 'Job')
    Job.objects.filter(name__in=[name for _, name in jobs]).delete()

def remove_initial_opportunity_type(apps, schema_editor):
    OpportunityType = apps.get_model('catalog', 'OpportunityType')
    OpportunityType.objects.filter(name__in=[name for _, name in opportunity_types]).delete()

def remove_initial_meeting_type(apps, schema_editor):
    MeetingType = apps.get_model('catalog', 'MeetingType')
    MeetingType.objects.filter(name__in=[name for _, name in meeting_types]).delete()

def remove_initial_meeting_result(apps, schema_editor):
    MeetingResult = apps.get_model('catalog', 'MeetingResult')
    MeetingResult.objects.filter(name__in=[name for _, name in meeting_results]).delete()

def remove_initial_lost_opportunity_type(apps, schema_editor):
    LostOpportunityType = apps.get_model('catalog', 'LostOpportunityType')
    LostOpportunityType.objects.filter(name__in=[name for _, name in lost_opportunity_types]).delete()

def remove_initial_purchase_status_type(apps, schema_editor):
    PurchaseStatusType = apps.get_model('catalog', 'PurchaseStatusType')
    PurchaseStatusType.objects.filter(name__in=[name for _, name in purchase_status_type]).delete()



# --- Configuración de la migración ---
class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(insert_initial_periods, reverse_code=remove_initial_periods),
        migrations.RunPython(insert_initial_cities, reverse_code=remove_initial_cities),
        migrations.RunPython(insert_initial_udns, reverse_code=remove_initial_udns),
        migrations.RunPython(insert_initial_business_groups, reverse_code=remove_initial_business_groups),
        migrations.RunPython(insert_initial_divisions, reverse_code=remove_initial_divisions),
        migrations.RunPython(insert_initial_subdivisions, reverse_code=remove_initial_subdivisions),
        migrations.RunPython(insert_initial_specialties, reverse_code=remove_initial_specialties),
        migrations.RunPython(insert_initial_project_statuses, reverse_code=remove_initial_project_statuses),
        migrations.RunPython(insert_initial_status_opportunities, reverse_code=remove_initial_status_opportunities),
        migrations.RunPython(insert_initial_currencies, reverse_code=remove_initial_currencies),
        migrations.RunPython(insert_initial_jobs, reverse_code=remove_initial_job),
        migrations.RunPython(insert_initial_opportunity_types, reverse_code=remove_initial_opportunity_type),
        migrations.RunPython(insert_initial_meeting_types, reverse_code=remove_initial_meeting_type),
        migrations.RunPython(insert_initial_meeting_results, reverse_code=remove_initial_meeting_result),
        migrations.RunPython(insert_initial_lost_opportunity_type, reverse_code=remove_initial_lost_opportunity_type),
        migrations.RunPython(insert_initial_purchase_status_type, reverse_code=remove_initial_purchase_status_type),
    ]