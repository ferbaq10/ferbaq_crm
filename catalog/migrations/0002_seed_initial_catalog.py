from django.db import migrations

periods = [
    "Primer Trimestre",
    "Segundo Trimestre",
    "Tercer Trimestre",
    "Cuarto Trimestre",
    "Primer Semestre",
    "Segundo Semestre",
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
    (3, "Fotovoltaica", 2),
]

specialities = [
    (1, "EPC"),
    (2, "MRO"),
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

def insert_initial_specialities(apps, schema_editor):
    Speciality = apps.get_model('catalog', 'Speciality')
    for id_val, name in specialities:
        Speciality.objects.update_or_create(id=id_val, defaults={'name': name})

def insert_initial_project_statuses(apps, schema_editor):
    ProjectStatus = apps.get_model('catalog', 'ProjectStatus')
    for id_val, name in project_statuses:
        ProjectStatus.objects.update_or_create(id=id_val, defaults={'name': name})

def insert_initial_status_opportunities(apps, schema_editor):
    StatusOpportunity = apps.get_model('catalog', 'StatusOpportunity')
    for id_val, name in status_opportunities:
        StatusOpportunity.objects.update_or_create(id=id_val, defaults={'name': name})

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

def remove_initial_specialities(apps, schema_editor):
    Speciality = apps.get_model('catalog', 'Speciality')
    Speciality.objects.filter(name__in=[name for _, name in specialities]).delete()

def remove_initial_project_statuses(apps, schema_editor):
    ProjectStatus = apps.get_model('catalog', 'ProjectStatus')
    ProjectStatus.objects.filter(name__in=[name for _, name in project_statuses]).delete()

def remove_initial_status_opportunities(apps, schema_editor):
    StatusOpportunity = apps.get_model('catalog', 'StatusOpportunity')
    StatusOpportunity.objects.filter(name__in=[name for _, name in status_opportunities]).delete()

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
        migrations.RunPython(insert_initial_specialities, reverse_code=remove_initial_specialities),
        migrations.RunPython(insert_initial_project_statuses, reverse_code=remove_initial_project_statuses),
        migrations.RunPython(insert_initial_status_opportunities, reverse_code=remove_initial_status_opportunities),
    ]