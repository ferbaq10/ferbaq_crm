from django.db import migrations
from django.conf import settings


def create_roles_and_permissions(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')
    ContentType = apps.get_model('contenttypes', 'ContentType')

    # Obtener modelo real del usuario
    auth_model = settings.AUTH_USER_MODEL  # Ej: 'users.User'
    app_label, model_name = auth_model.split(".")

    # Crear grupos (roles)
    roles = {
        'Director Comercial': [],
        'Gerente Comercial': [],
        'Vendedor': [],
        'Comprador': [],
    }

    for role_name in roles.keys():
        group, _ = Group.objects.get_or_create(name=role_name)
        roles[role_name] = group

    # Obtener permisos del modelo User (o el que tengas personalizado)
    try:
        ct = ContentType.objects.get(app_label=app_label, model=model_name.lower())
    except ContentType.DoesNotExist:
        print(f"⚠️ ContentType {app_label}.{model_name} no encontrado.")
        return

    perms = Permission.objects.filter(content_type=ct)

    for perm in perms:
        # Asignar permisos según rol
        if perm.codename.startswith('view_'):
            roles['Director Comercial'].permissions.add(perm)
            roles['Gerente Comercial'].permissions.add(perm)


def remove_roles_and_permissions(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')
    ContentType = apps.get_model('contenttypes', 'ContentType')

    group_names = ['Director Comercial', 'Gerente Comercial', 'Vendedor', 'Comprador']

    auth_model = settings.AUTH_USER_MODEL
    app_label, model_name = auth_model.split(".")

    try:
        ct = ContentType.objects.get(app_label=app_label, model=model_name.lower())
        perms = Permission.objects.filter(content_type=ct)
    except ContentType.DoesNotExist:
        perms = []

    for group_name in group_names:
        try:
            group = Group.objects.get(name=group_name)
            group.permissions.remove(*perms)
        except Group.DoesNotExist:
            continue


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.RunPython(create_roles_and_permissions, remove_roles_and_permissions),
    ]