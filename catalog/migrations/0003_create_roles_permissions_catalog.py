from django.db import migrations


# Modelos de catálogo (todos del mismo módulo)
model_names = [
    'UDN', 'WorkCell', 'BusinessGroup', 'Division', 'Subdivision', 'Specialty',
    'ProjectStatus', 'City', 'Period', 'StatusOpportunity', 'Currency', 'Job',
    'OpportunityType', 'MeetingType', 'MeetingResult', 'LostOpportunityType', 'PurchaseStatusType'
]

app_label='catalog'


def create_roles_and_permissions(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')
    ContentType = apps.get_model('contenttypes', 'ContentType')

    # Crear permisos sin modelo asociado
    generic_ct = ContentType.objects.get_for_model(Permission)

    # Crear grupos
    roles = {
        'Director Comercial': [],
        'Gerente Comercial': [],
        'Vendedor': [],
        'Comprador': [],
    }

    # Permiso: view_dashboard
    view_dashboard_perm, _ = Permission.objects.get_or_create(
        codename='view_dashboard',
        name='Puede ver el dashboard',
        content_type=generic_ct
    )

    # Permiso: view_catalog
    view_catalog_perm, _ = Permission.objects.get_or_create(
        codename='view_catalog',
        name='Puede ver el catálogo',
        content_type=generic_ct
    )

    for role_name in roles.keys():
        group, _ = Group.objects.get_or_create(name=role_name)
        roles[role_name] = group

    # Crear permisos y asignarlos a los grupos
    for model_name in model_names:
        ct = ContentType.objects.get(app_label=app_label, model=model_name.lower())

        perms = Permission.objects.filter(content_type=ct)

        for perm in perms:
            # Director: todos los permisos
            roles['Director Comercial'].permissions.add(perm)

            # Gerente Comercial: ver, agregar y cambiar
            if perm.codename.startswith(('view_', 'add_', 'change_')):
                roles['Gerente Comercial'].permissions.add(perm)

            # Vendedor: sin permisos en estos modelos

            # Comprador: sin permisos en estos modelos

        # Asignar view_dashboard a todos los roles
        for group in roles.values():
            group.permissions.add(view_dashboard_perm)

        # Asignar view_catalog a todos excepto Vendedor y Comprador
        for role_name in ['Director Comercial', 'Gerente Comercial']:
            roles[role_name].permissions.add(view_catalog_perm)

def remove_roles_and_permissions(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')
    ContentType = apps.get_model('contenttypes', 'ContentType')

    generic_ct = ContentType.objects.get_for_model(Permission)

    group_names = ['Director Comercial', 'Gerente Comercial', 'Vendedor', 'Comprador']

    for group_name in group_names:
        try:
            group = Group.objects.get(name=group_name)
        except Group.DoesNotExist:
            continue

        for model_name in model_names:
            try:
                ct = ContentType.objects.get(app_label=app_label, model=model_name.lower())
                perms = Permission.objects.filter(content_type=ct)
                group.permissions.remove(*perms)
            except ContentType.DoesNotExist:
                continue

    # Eliminar permisos view_dashboard y view_catalog
    try:
        view_dashboard_perm = Permission.objects.get(codename='view_dashboard', content_type=generic_ct)
        view_catalog_perm = Permission.objects.get(codename='view_catalog', content_type=generic_ct)
    except Permission.DoesNotExist:
        return

    for group_name in group_names:
        try:
            group = Group.objects.get(name=group_name)
            group.permissions.remove(view_dashboard_perm, view_catalog_perm)
        except Group.DoesNotExist:
            continue


class Migration(migrations.Migration):

    dependencies = [
        (app_label, '0002_seed_initial_catalog'),
        ('auth', '0012_alter_user_first_name_max_length'),  # Ajusta según tu historial
    ]

    operations = [
        migrations.RunPython(create_roles_and_permissions, remove_roles_and_permissions),
    ]
