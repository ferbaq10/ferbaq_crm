from django.db import migrations

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

work_cells = [
    (1, "Célula 1"),
    (2, "Célula 2"),
    (3, "Célula 3"),
    (4, "Célula 4"),
    (5, "Célula 5"),
    (6, "Célula 6"),
    (7, "Célula 7"),
    (8, "Célula 8"),
    (9, "Célula 9"),
    (10, "Célula 10"),
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
    (1, "Iniciado"),
    (2, "En curso"),
    (3, "Por terminar"),
    (4, "Finalizado"),
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

def insert_initial_work_cells(apps, schema_editor):
    WorkCell = apps.get_model('catalog', 'WorkCell')
    for id_val, name in work_cells:
        WorkCell.objects.update_or_create(id=id_val, defaults={'name': name})

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

# --- Eliminaciones ---
def remove_initial_periods(apps, schema_editor):
    Period = apps.get_model('catalog', 'Period')
    Period.objects.filter(name__in=periods).delete()

def remove_initial_cities(apps, schema_editor):
    City = apps.get_model('catalog', 'City')
    City.objects.filter(name__in=cities).delete()

def remove_initial_udns(apps, schema_editor):
    UDN = apps.get_model('catalog', 'UDN')
    UDN.objects.filter(name__in=[name for _, name in udns]).delete()

def remove_initial_work_cells(apps, schema_editor):
    WorkCell = apps.get_model('catalog', 'WorkCell')
    WorkCell.objects.filter(name__in=[name for _, name in work_cells]).delete()

def remove_initial_business_groups(apps, schema_editor):
    BusinessGroup = apps.get_model('catalog', 'BusinessGroup')
    BusinessGroup.objects.filter(name__in=[name for _, name in business_groups]).delete()

def remove_initial_divisions(apps, schema_editor):
    Division = apps.get_model('catalog', 'Division')
    Division.objects.filter(name__in=[name for _, name in divisions]).delete()

def remove_initial_subdivisions(apps, schema_editor):
    Subdivision = apps.get_model('catalog', 'Subdivision')
    Subdivision.objects.filter(name__in=[name for _, name, _ in subdivisions]).delete()

def remove_initial_specialties(apps, schema_editor):
    Specialty = apps.get_model('catalog', 'Specialty')
    Specialty.objects.filter(name__in=[name for _, name in specialties]).delete()

def remove_initial_project_statuses(apps, schema_editor):
    ProjectStatus = apps.get_model('catalog', 'ProjectStatus')
    ProjectStatus.objects.filter(name__in=[name for _, name in project_statuses]).delete()

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
    OpportunityType.objects.filter(name__in=[name for _, name in jobs]).delete()

def remove_initial_meeting_type(apps, schema_editor):
    MeetingType = apps.get_model('catalog', 'MeetingType')
    MeetingType.objects.filter(name__in=[name for _, name in jobs]).delete()

def remove_initial_meeting_result(apps, schema_editor):
    MeetingResult = apps.get_model('catalog', 'MeetingResult')
    MeetingResult.objects.filter(name__in=[name for _, name in jobs]).delete()



# --- Configuración de la migración ---
class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(insert_initial_periods, reverse_code=remove_initial_periods),
        migrations.RunPython(insert_initial_cities, reverse_code=remove_initial_cities),
        migrations.RunPython(insert_initial_udns, reverse_code=remove_initial_udns),
        migrations.RunPython(insert_initial_work_cells, reverse_code=remove_initial_work_cells),
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
    ]